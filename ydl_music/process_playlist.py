import logging
import time

from ydl_music import utils
from ydl_music.process_video import process_video

logger = logging.getLogger(__name__)
_ROOT = "D:/Musik"


def process_playlist(videos: dict) -> None:
    """Process an entire playlist of videos. A long list can lead to problems as youtube will limit traffic."""
    for vid_id, vid_conf in videos.items():
        logger.info(f"Process video id '{vid_id}'")
        process_video(vid_id, **vid_conf, open_folder=False)
        time.sleep(60)


if __name__ == "__main__":
    utils.setup_logging()
    # TODO: read from file and consider DQ checks
    dummy_example = {
        "aaaaaaaaaaa": {"custom_title": "band - album (year)"},
        "bbbbbbbbbbb": {
            # to be read from separate csv's (not supported yet, custom_title and edit_times fit my cases so far)
            "custom_chapters": [
                {"start_time": 00, "end_time": 99, "title": "1"},
                {"start_time": 100, "end_time": 666, "title": "2"},
            ]
        },
        "ccccccccccc": {"edit_times": True},
    }
    process_playlist(dummy_example)
