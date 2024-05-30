import logging
import sys

from ydl_music.process_video import process_video

logger = logging.getLogger(__name__)
_ROOT = "D:/Musik"


def process_playlist(videos: dict) -> None:
    for vid_id, vid_conf in videos.items():
        logger.info(f"Process video id '{vid_id}'")
        process_video(vid_id, **vid_conf)


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s: [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    root.addHandler(handler)
    # TODO: define input + logic to automate this (without custom chapters for now to keep a simple csv structure)
    dummy_example = {
        "aaaaaaaaaaa": {"custom_title": "band - album (year)"},
        "bbbbbbbbbbb": {
            "custom_chapters": [
                # or define this in another csv?
                {"start_time": 00, "end_time": 99, "title": "1"},
                {"start_time": 100, "end_time": 666, "title": "2"},
            ]
        },
    }
    process_playlist(dummy_example)
