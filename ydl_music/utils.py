import json
import logging
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
