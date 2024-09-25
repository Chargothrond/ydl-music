import os
import subprocess
from pathlib import Path
from ydl_music import utils


def overlap_tracks(input_files, output_folder, overlap_duration=5):
    """Overlap MP3 tracks by moving start of the next track onto the previous one."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process each pair of consecutive tracks
    for i in range(len(input_files) - 1):
        input_file_1 = input_files[i]
        input_file_2 = input_files[i + 1]

        output_file = output_folder / os.path.basename(input_file_1)

        # Use ffmpeg to trim the second track and merge it with the first
        cmd = " ".join([
            'ffmpeg',
            '-i', str(input_file_1),            # Input track 1
            '-i', str(input_file_2),            # Input track 2
            '-filter_complex', f'[1]atrim=0:{overlap_duration},asetpts=PTS-STARTPTS[overlap];'
                               f'[0][overlap]amix=inputs=2:duration=first',  # Mix first second of track 2 into track 1
            '-c:a', 'libmp3lame',          # Use MP3 encoding
            '-q:a', '2',                   # Set the quality level for output MP3
            r'-hide_banner', r'-loglevel warning',
            str(output_file),
        ])
        fc_str1 = f'[1]atrim=0:{overlap_duration},asetpts=PTS-STARTPTS[overlap];'
        fc_str2 = f'[0][overlap]amix=inputs=2:duration=first'
        suffix = '-c:a libmp3lame -q:a 2 -hide_banner -loglevel warning'
        cmd = f'ffmpeg -i {input_file_1} -i  {input_file_2} -filter_complex {fc_str1}{fc_str2} {suffix}'
        print(f"cmd: {cmd}")

        subprocess.run(cmd, shell=True)
        print(f"Processed {input_file_1} and {input_file_2} -> {output_file}")


if __name__ == "__main__":
    utils.setup_logging()
    inp_files = list(Path("D:/Musik/Albinobeach/test").glob("*.mp3"))  # rely on implicit order initially
    out_folder = "D:/Musik/Albinobeach/test2"
    overlap_tracks(inp_files, out_folder)
