import os
import subprocess

def overlap_tracks(input_files, output_folder, overlap_duration=1):
    """
    Overlap MP3 tracks by moving the first second of the next track onto the previous one.

    Args:
        input_files (list): List of input MP3 file paths.
        output_folder (str): Path to the output folder.
        overlap_duration (int): Overlap duration in seconds (default is 1 second).
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process each pair of consecutive tracks
    for i in range(len(input_files) - 1):
        input_file_1 = input_files[i]
        input_file_2 = input_files[i + 1]

        # Create output filename
        base_filename = os.path.basename(input_file_1)
        output_file = os.path.join(output_folder, f"output_{base_filename}")

        # Use ffmpeg to trim the second track and merge it with the first
        cmd = [
            'ffmpeg',
            '-i', input_file_1,            # Input track 1
            '-i', input_file_2,            # Input track 2
            '-filter_complex', f'[1]atrim=0:{overlap_duration},asetpts=PTS-STARTPTS[overlap];'
                               f'[0][overlap]amix=inputs=2:duration=first',  # Mix first second of track 2 into track 1
            '-c:a', 'libmp3lame',          # Use MP3 encoding
            '-q:a', '2',                   # Set the quality level for output MP3
            output_file
        ]

        # Execute the ffmpeg command
        subprocess.run(cmd, check=True)
        print(f"Processed {input_file_1} and {input_file_2} -> {output_file}")

# Example usage
input_files = ['track1.mp3', 'track2.mp3', 'track3.mp3']  # List your MP3 files here
output_folder = 'output_tracks'

overlap_tracks(input_files, output_folder)
