import json
import logging
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Sequence, Union

# see https://github.com/ytdl-org/youtube-dl/#readme for youtube_dl usage
import youtube_dl  # noqa (its CLI is called via subprocess)

_DEFAULTS = {
    "info_keys": ["title", "description", "duration", "chapters"],
    "sep_band": r" - ",
    "sep_album": r" \(",
}
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)


def process_single_video(vid: str, custom_chapters: Optional[list[dict]] = None) -> None:
    yt_url = f"https://youtu.be/{vid}"
    logger.info(f"Download {yt_url}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        target = rf"{tmp_dir}\%(title)s.%(ext)s"
        cmd = f'youtube-dl {yt_url} -o "{target}" -x --audio-format mp3 --audio-quality 192K --write-info-json'
        # wanted to use the Python interface directly, but getting info_dict is more cumbersome than with the CLI
        subprocess.run(cmd, shell=True)
        logger.info(f"Finished downloading {yt_url}")
        # there will be just one such file thanks to the temporary directory
        info_json = [fp for fp in Path(tmp_dir).iterdir() if fp.suffixes == [".info", ".json"]][0]
        vid_info = get_json_info(info_json)
        band, album, year = parse_title(vid_info["title"])
        chapters = get_chapters(vid_info, custom_chapters)
        if len(chapters) == 1:
            # TODO: Copy single file and rename + set metadata
            print("todo")
        else:
            # TODO: use ffmpeg CLI to split chapters into tracks, copy over + set metadata
            print("todo")
        logger.info("Done")

    # "chapters" keys: {"start_time": 0.0, "end_time": 276.0, "title": "Track 01"}


def get_json_info(json_fp: Path, keys_to_keep: Union[Sequence[str], None] = None) -> dict:
    logger.info(f"Get metadata information from {json_fp}")
    if keys_to_keep is None:
        keys_to_keep = _DEFAULTS["info_keys"]
    with open(json_fp) as jf:
        info_dict = json.load(jf)
    return {k: v for k, v in info_dict.items() if k in keys_to_keep}


def parse_title(title: str) -> tuple[str, str, str]:
    logger.info(f"Parse (band, album, year) from {title}")
    regex = r"^(.*)" + _DEFAULTS["sep_band"] + r"(.*)" + _DEFAULTS["sep_album"] + r".*([0-9]{4}).*$"  # type: ignore
    res = re.findall(regex, title)
    if len(res) == 0:
        raise ValueError(f"Could not match fields from regex '{regex}' for title: {title}")
    return res[0]


def get_chapters(vid_info: dict, custom_chapters: Optional[list[dict]] = None) -> list[dict]:
    logger.info("Get chapters / track information")
    if custom_chapters:
        logger.info("Using custom chapters instead of derived ones")
        return custom_chapters
    if "chapters" not in vid_info.keys():
        logger.warning("Video lacks chapters, check if just one track or if they need to be passed manually instead")
        return [{}]
    return vid_info["chapters"]


if __name__ == "__main__":
    process_single_video("1vgDD9BIXo8")  # 7ZyDQYcz_Vo
