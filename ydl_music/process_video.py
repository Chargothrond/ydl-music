import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

# see https://github.com/ytdl-org/youtube-dl/#readme for youtube_dl usage
import youtube_dl  # noqa (its CLI is called via subprocess)

from ydl_music import utils

logger = logging.getLogger(__name__)
_ROOT = "D:/Musik"


def process_video(
    vid: str, custom_title: Optional[str] = None, custom_chapters: Optional[list[dict]] = None
) -> None:
    yt_url = f"https://youtu.be/{vid}"

    with tempfile.TemporaryDirectory() as tmp_dir:
        logger.info(f"Download {yt_url}")
        mp3_inp, vid_info = utils.download_video(yt_url, tmp_dir)
        band, album, year = utils.parse_title(custom_title if custom_title else vid_info["title"])

        if custom_chapters:
            logger.info("Using custom chapters instead of derived ones")
            # TODO: dq check structure (keys: "start_time", "end_time" and "title")
            chapters = custom_chapters
        else:
            logger.info("Get chapters / track information")
            chapters = utils.get_chapters(vid_info)

        logger.info(f"Creating folders for band '{band}' and album '{album}'")
        band_dir = utils.add_folder_if_needed(Path(_ROOT), band)
        album_dir = utils.add_folder_if_needed(band_dir, album)
        os.startfile(album_dir)

        if len(chapters) == 1:
            utils.copy_track_with_md(mp3_inp, album_dir, band, album, album, "01", year)
        else:
            chapters = utils.remove_title_prefixes(chapters)
            for idx, chapter in enumerate(chapters, start=1):
                # this should never go into 3 digits and 001 would look stranger than 01
                track = f"0{idx}" if idx < 10 else f"{idx}"
                utils.copy_track_with_md(mp3_inp, album_dir, band, album, chapter["title"], track, year, chapter)

    logger.info("Done")


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s: [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    root.addHandler(handler)
    process_video("aaaaaaaaa")  # , custom_title="Band - Album (year)"
