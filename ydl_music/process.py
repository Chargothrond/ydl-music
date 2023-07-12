import logging
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

# see https://github.com/ytdl-org/youtube-dl/#readme for youtube_dl usage
import youtube_dl  # noqa (its CLI is called via subprocess)

from ydl_music import utils

logger = logging.getLogger(__name__)


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
        vid_info = utils.get_json_info(info_json)
        band, album, year = utils.parse_title(vid_info["title"])
        chapters = utils.get_chapters(vid_info, custom_chapters)
        if len(chapters) == 1:
            # TODO: Copy single file and rename + set metadata
            print("todo")
        else:
            # TODO: use ffmpeg CLI to split chapters into tracks, copy over + set metadata
            print("todo")
        logger.info("Done")

    # "chapters" keys: {"start_time": 0.0, "end_time": 276.0, "title": "Track 01"}


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s: [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    root.addHandler(handler)
    process_single_video("1vgDD9BIXo8")  # 7ZyDQYcz_Vo
