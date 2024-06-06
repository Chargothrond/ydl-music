import logging
import time
from pathlib import Path

import pandas as pd

from ydl_music import utils
from ydl_music.process_video import process_video

logger = logging.getLogger(__name__)
_ROOT = "D:/Musik"


def process_playlist(inp: Path) -> None:
    """Process an entire playlist of videos. A long list can lead to problems as youtube will limit traffic."""
    # this can be made more robust, consider also DQ checks
    videos = pd.read_csv(inp, dtype=str, keep_default_na=False)
    process_video_option_cols = ["custom_title", "custom_chapters", "edit_times"]
    videos = videos[["yid", *process_video_option_cols]]
    logger.info(f"Processing {len(videos)} video ids")
    for index, row in videos.iterrows():
        vid_id = row["yid"]
        vid_conf = dict(row[process_video_option_cols])
        vid_conf["edit_times"] = bool(row["edit_times"])
        process_video(vid_id, **vid_conf, open_folder=False)
        time.sleep(60)
    logger.info("Finished processing video ids")


if __name__ == "__main__":
    utils.setup_logging()
    process_playlist(Path(__file__).parent.parent / "music_list.csv")
