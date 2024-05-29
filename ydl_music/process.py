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


def process_single_video(vid: str, custom_chapters: Optional[list[dict]] = None) -> None:
    yt_url = f"https://youtu.be/{vid}"

    with tempfile.TemporaryDirectory() as tmp_dir:
        logger.info(f"Download {yt_url}")
        mp3_inp, vid_info = utils.download_video(yt_url, tmp_dir)
        band, album, year = utils.parse_title(vid_info["title"])

        if custom_chapters:
            logger.info("Using custom chapters instead of derived ones")
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
            for idx, chapter in enumerate(chapters):
                idx = idx + 1
                title = utils.remove_title_prefixes(chapter["title"], idx)
                # this should never go into 3 digits and 001 would look stranger than 01
                track = f"0{idx}" if idx < 10 else f"{idx}"
                utils.copy_track_with_md(mp3_inp, album_dir, band, album, title, track, year, chapter)
    # store info in log?
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
    # process_single_video("VxQBM6e94I4")  # 26min test video, album with just one song and no chapters
    process_single_video("2fFzjLYEj50")
