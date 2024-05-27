import json
import logging
import os
import re
from pathlib import Path
from typing import Optional, Sequence, Union

logger = logging.getLogger(__name__)
_DEFAULTS = {
    "info_keys": ["title", "description", "duration", "chapters"],
    "sep_band": r" - ",
    "sep_album": r" \(",
}


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
        logger.warning(f"Could not match fields from regex '{regex}' for title '{title}', provide manually")
        title = input("Paste video title that can be parsed instead (i.e. matching expectation from regex): ")
        res = re.findall(regex, title)
        if len(res) == 0:
            raise ValueError("Wrong input, try again from start")
        return res[0]
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


def prep_md_string(title: str, band: str, album: str, track: str, year: str) -> str:
    res = "-metadata " + " -metadata ".join(
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
    return res


def add_folder_if_needed(dir_to_create: Path):
    if not dir_to_create.exists():
        logger.info(f"There is no folder for band / album '{dir_to_create.parts[-1]}' yet, creating it")
        os.mkdir(dir_to_create)


def get_target_path(album_folder: Path, title: str) -> Path:
    target_mp3 = album_folder / f"{title}.mp3"
    if target_mp3.exists():
        raise FileExistsError(f"{target_mp3} already exists!")
    return target_mp3
