import json
import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)
_DEFAULTS = {
    "info_keys": ["title", "description", "duration", "chapters"],
    "sep_band": r" - ",
    "sep_album": r" \(",
    "ffmpeg_opts": r"-hide_banner -loglevel warning",
}


def download_video(yt_url: str, tmp_dir: str) -> Tuple[Path, dict]:
    tmp_path = Path(tmp_dir)
    tf = "tmp_file"
    target = rf"{tmp_path}\{tf}.%(ext)s"
    # wanted to use the Python interface directly, but getting info_dict is more cumbersome than with the CLI
    cmd = f'youtube-dl {yt_url} -o "{target}" -x --audio-format mp3 --audio-quality 192K --write-info-json'
    subprocess.run(cmd, shell=True)
    logger.info(f"Finished downloading {yt_url}")
    mp3_fp = tmp_path / f"{tf}.mp3"
    json_fp = tmp_path / f"{tf}.info.json"
    logger.info(f"Get metadata information from {json_fp}")
    with open(json_fp) as jf:
        info_dict = {k: v for k, v in json.load(jf).items() if k in _DEFAULTS["info_keys"]}
    return mp3_fp, info_dict


def parse_title(title: str, force_custom_title: Optional[bool] = False) -> tuple[str, str, str]:
    logger.info(f"Parse (band, album, year) from {title}")
    regex = r"^(.*)" + _DEFAULTS["sep_band"] + r"(.*)" + _DEFAULTS["sep_album"] + r".*([0-9]{4}).*$"  # type: ignore
    res = re.findall(regex, title)
    if force_custom_title or len(res) == 0:
        if len(res) == 0:
            logger.warning(f"Could not match fields from regex '{regex}' for title '{title}', provide manually")
        title = input("Paste video title that can be parsed instead (i.e. matching expectation from regex): ")
        res = re.findall(regex, title)
        if len(res) == 0:
            raise ValueError("Wrong input, try again from start")
        return res[0]
    return res[0]


def add_folder_if_needed(root: Path, folder_name: str) -> Path:
    dir_to_create = Path(root) / folder_name
    if not dir_to_create.exists():
        logger.info(f"There is no folder for band / album '{dir_to_create.parts[-1]}' yet, creating it")
        os.mkdir(dir_to_create)
    return dir_to_create


def get_chapters(vid_info: dict) -> list[dict]:
    if "chapters" not in vid_info.keys():
        logger.warning("Video lacks chapters, check if just one track or if they need to be passed manually instead")
        return [{}]
    return vid_info["chapters"]


def remove_title_prefixes(chapters: list[dict]) -> list[dict]:
    for idx, chapter in enumerate(chapters, start=1):
        # TODO: this can be improved, but is tricky as many different conventions might exist
        chapter["title"] = re.sub(rf"^0{idx}\.? ", "", chapter["title"])  # "01. title" and "01 title"
        chapter["title"] = re.sub(rf"^{idx}\. ", "", chapter["title"])  # "1. title" (not "1 title" on purpose for now)
        chapters[idx - 1] = chapter
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
    logger.info("Defining metadata and options for ffmpeg")
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
    logger.info(f"Running ffmpeg: {cmd}")
    subprocess.run(cmd, shell=True)
    logger.info(f"Finished saving track '{title}'")
