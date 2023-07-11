import logging
import subprocess
# see https://github.com/ytdl-org/youtube-dl/#readme for youtube_dl usage
import youtube_dl  # noqa (its CLI is called via subprocess)

logger = logging.getLogger(__name__)


def playground(vid):
    yt_url = f"https://youtu.be/{vid}"
    logger.info(f"Downloading {yt_url}")

    # TODO: use tmpdir, make sure download gets stored there, use .info.json extensions to get info and
    #  relevant fields. next: extract (interpret, album, year) from title with regex, use ffmpeg CLI to
    #  split chapters into tracks, save / organize results (ideally incl. all relevant .mp3 metadata)

    # wanted to use the Python interface directly, but getting info_dict is more cumbersome than with the CLI
    cmd = f"youtube-dl {yt_url} -x --audio-format mp3 --audio-quality 192K --write-info-json"
    subprocess.run(cmd, shell=True)

    # useful json keys: "title", "description" (ref / dq), "duration" (ref / dq), "chapters"
    # "chapters" is a list of dicts with these keys each (time is in seconds):
    #   {"start_time": 0.0, "end_time": 276.0, "title": "Track 01"}


if __name__ == "__main__":
    playground("7ZyDQYcz_Vo")  # 1vgDD9BIXo8
