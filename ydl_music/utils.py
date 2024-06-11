import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

# see https://github.com/ytdl-org/youtube-dl/#readme for youtube_dl usage
import youtube_dl  # noqa (its CLI is called via subprocess)

logger = logging.getLogger(__name__)
_DEFAULTS = {
    "info_keys": ["title", "description", "duration", "chapters"],
    "sep_band": r" - ",
    "sep_album": r" \(",
    "ffmpeg_opts": r"-hide_banner -loglevel warning",
}


def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s: [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    root.addHandler(handler)


def download_video(yt_url: str, tmp_dir: str) -> Tuple[Path, dict]:
    """Downloads a video using the `youtube-dl` CLI. Also downloads a json file containing relevant metadata."""
    tmp_path = Path(tmp_dir)
    tf = "tmp_file"
    target = rf"{tmp_path}\{tf}.%(ext)s"
    # wanted to use the Python interface directly, but getting info_dict is more cumbersome than with the CLI
    cmd = f'youtube-dl {yt_url} -o "{target}" -x --audio-format mp3 --audio-quality 192K --write-info-json'
    subprocess.run(cmd, shell=True)
    logger.info(f"Finished downloading {yt_url}")
    mp3_fp = tmp_path / f"{tf}.mp3"
    json_fp = tmp_path / f"{tf}.info.json"
    logger.debug(f"Get metadata information from {json_fp}")
    with open(json_fp) as jf:
        info_dict = {k: v for k, v in json.load(jf).items() if k in _DEFAULTS["info_keys"]}
    return mp3_fp, info_dict


def parse_title(title: str) -> tuple[str, ...]:
    """Parse information from the video title. Expects format `band - album (year)`. Asks for manual input if needed."""
    logger.debug(f"Parse (band, album, year) from {title}")
    regex = r"^(.*)" + _DEFAULTS["sep_band"] + r"(.*)" + _DEFAULTS["sep_album"] + r".*([0-9]{4}).*$"  # type: ignore
    res = re.findall(regex, title)
    if len(res) == 0:
        logger.warning(f"Could not match fields from regex '{regex}' for title '{title}', provide manually")
        title = input("Paste video title that can be parsed instead (i.e. matching expectation from regex): ")
        res = re.findall(regex, title)
        if len(res) == 0:
            raise ValueError("Wrong input, try again from start")
        return res[0]
    # sometimes these youtube metadata fields have trailing whitespaces
    res = tuple([re.sub(r"\s+$", "", info) for info in res[0]])
    return res


def add_folder_if_needed(root: Path, folder_name: str) -> Path:
    """Creates new folders per band or album if required."""
    dir_to_create = Path(root) / folder_name
    if not dir_to_create.exists():
        logger.warning(f"Creating new folder for: '{dir_to_create.parts[-1]}'")
        os.mkdir(dir_to_create)
    return dir_to_create


def get_chapters(vid_info: dict) -> list[dict]:
    """Gets chapter information from the video if it exists. Otherwise returns a list with one empty dictionary."""
    logger.debug("Get chapters / track information")
    if "chapters" not in vid_info.keys():
        logger.warning("Video lacks chapters, check if just one track or if they need to be passed manually instead")
        return [{}]
    return vid_info["chapters"]


def clean_song_titles(chapters: list[dict]) -> list[dict]:
    """Cleans song titles based on known patterns. Edit corner cases manually or use custom chapters."""
    for idx, chapter in enumerate(chapters, start=1):
        # add new conventions when they occur, although this will always be error-prone for certain cases (pass
        # custom_chapters to process_video instead which will skip this function)
        # deal with track number prefixes
        # "01. - title", "01 - title", "1. - title", "1 - title"
        chapter["title"] = re.sub(rf"^0?{idx}\.? - ", "", chapter["title"])
        # "01. title" and "01 title"
        chapter["title"] = re.sub(rf"^0{idx}\.? ", "", chapter["title"])
        # "1. title" (not "1 title" on purpose because sometimes song titles are just numbers)
        chapter["title"] = re.sub(rf"^{idx}\. ", "", chapter["title"])
        # deal with trailing time stamps in titles (stripping off e.g. 04:20, but also 4:20:00 or 04:20:00)
        chapter["title"] = re.sub(r" [0-9]?[0-9]?:?[0-9]{2}:[0-9]{2}", "", chapter["title"])
        chapters[idx - 1] = chapter
    return chapters


def edit_times(chapters: list[dict]) -> list[dict]:
    """Interactive way to modify track times."""
    # this can be improved, but is less effort than creating a full custom_chapters csv
    logger.info("Edit track times as required, as integers in seconds (or empty to keep default)")
    for idx, chapter in enumerate(chapters):
        for time in ["start_time", "end_time"]:
            orig_t = chapter[time]
            user_t = input(f"New {time} (in seconds) instead of '{orig_t}' (empty = use default): ")
            if len(user_t) > 0:
                chapter[time] = int(user_t)
        chapters[idx] = chapter
    return chapters


def copy_track_with_md(
    mp3_inp: Path,
    out_dir: Path,
    band: str,
    album: str,
    title: str,
    track: str,
    year: str,
    chapter: Optional[dict] = None,
) -> None:
    """Calls the `ffmpeg` CLI with relevant metadata and options."""
    logger.debug("Defining metadata and options for ffmpeg")
    md = "-metadata " + " -metadata ".join(
        [
            f'{k}="{v}"'
            for k, v in {
                "title": title,
                "artist": band,
                "album_artist": band,
                "album": album,
                "track": track,
                "date": year,
            }.items()
        ]
    )
    segment = f'-ss {chapter["start_time"]} -to {chapter["end_time"]}' if chapter else ""
    fp_save_title = re.sub(r"[^\w\s-]", "_", title)
    target_mp3 = out_dir / f"{track} {fp_save_title}.mp3"
    if target_mp3.exists():
        raise FileExistsError(f"{target_mp3} already exists!")
    cmd = f'ffmpeg -i {mp3_inp} {md} {segment} -codec copy "{target_mp3}" {_DEFAULTS["ffmpeg_opts"]}'
    logger.debug(f"Running ffmpeg: {cmd}")
    subprocess.run(cmd, shell=True)
    logger.info(f"Finished saving track '{title}'")
