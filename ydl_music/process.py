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
_ROOT = "D:/Musik"


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

        band_folder = Path(_ROOT) / band
        utils.add_folder_if_needed(band_folder)
        album_folder = band_folder / album
        utils.add_folder_if_needed(album_folder)
        chapters = utils.get_chapters(vid_info, custom_chapters)
        ffmpeg_opts = "-hide_banner -loglevel warning"
        if len(chapters) == 1:
            md = utils.prep_md_string(album, band, album, "01", year)
            target_mp3 = utils.get_target_path(album_folder, f"01 {album}")
            cmd = f'ffmpeg -i {mp3_inp} {md} -codec copy "{target_mp3}" {ffmpeg_opts}'
            subprocess.run(cmd, shell=True)
        else:
            for idx, chapter in enumerate(chapters):
                idx = idx + 1
                st = chapter["start_time"]
                et = chapter["end_time"]
                title = chapter["title"]
                # TODO: automate this more. occurred patterns (so far): "1. title", "01. title", "01 title"
                title = title.replace(f"0{idx}. ", "")
                track = f"0{idx}" if idx < 10 else f"{idx}"  # this should never go above 99
                target_mp3 = utils.get_target_path(album_folder, f"{track} {title}")
                md = utils.prep_md_string(title, band, album, track, year)
                cmd = f'ffmpeg -i {mp3_inp} {md} -ss {st} -to {et} -codec copy "{target_mp3}" {ffmpeg_opts}'
                subprocess.run(cmd, shell=True)
    logger.info("Done")


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s: [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    root.addHandler(handler)
    # process_single_video("7ZyDQYcz_Vo")  # 2min test video (not fitting expected structure)
    # process_single_video("1vgDD9BIXo8")  # 12min test video, but longer test video fitting target structure
    # process_single_video("VxQBM6e94I4")  # 26min text video, album with just one song and no chapters
    process_single_video("kaHq5xM4i_s")
