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
        tmp_path = Path(tmp_dir)
        tf = "tmp_file"
        target = rf"{tmp_path}\{tf}.%(ext)s"
        cmd = f'youtube-dl {yt_url} -o "{target}" -x --audio-format mp3 --audio-quality 192K --write-info-json'
        # wanted to use the Python interface directly, but getting info_dict is more cumbersome than with the CLI
        subprocess.run(cmd, shell=True)
        logger.info(f"Finished downloading {yt_url}")
        mp3_inp = tmp_path / f"{tf}.mp3"
        vid_info = utils.get_json_info(tmp_path / f"{tf}.info.json")
        band, album, year = utils.parse_title(vid_info["title"])
        chapters = utils.get_chapters(vid_info, custom_chapters)
        if len(chapters) == 1:
            # TODO: rename / copy track to target, (set track number) and other metadata
            print("todo")
        else:
            for chapter in chapters:
                st = chapter["start_time"]
                et = chapter["end_time"]
                track = chapter["title"]
                tmp_track = tmp_path / "tmp_track.mp3"
                cmd = f"ffmpeg -i {mp3_inp} -ss {st} -to {et} -c copy {tmp_track}"
                subprocess.run(cmd, shell=True)
                # TODO: rename / copy track to target, set track number and other metadata
    logger.info("Done")


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s: [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    root.addHandler(handler)
    process_single_video("1vgDD9BIXo8")  # 7ZyDQYcz_Vo
