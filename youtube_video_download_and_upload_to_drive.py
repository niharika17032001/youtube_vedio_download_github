import os
from time import sleep

import yt_dlp

import ImportantVariables as imp_val
import download_folder_from_drive
import upload_folder_to_drive
import video_download

video_directory = imp_val.downloaded_videos_folder
output_videos_folder = imp_val.create_output_videos_folder()


def validate_vedio_files(video_files):
    try:
        if not video_files:
            raise ValueError("No video files found in the specified directory.")
        else:
            print(f"Found {len(video_files)} video files: {video_files}")
    except ValueError as e:
        print(e)


def attempt_video_download(index):
    try:
        video_download.main(index)

    except yt_dlp.utils.DownloadError as e:
        print(f"Download failed: {e}")
        # Handle the error or retry logic here


# Example usage


def main(index):
    download_folder_from_drive.main()

    attempt_video_download(index)

    #
    sleep(1)
    all_files=[]
    for folder_name in os.listdir(video_directory):
        folder_path = os.path.join(video_directory, folder_name)
        if os.path.isdir(folder_path):  # Only include directories
            files = os.listdir(folder_path)
            all_files.extend(files)
    print("All files in the directory:", all_files)
    # Get all video files
    print(video_directory)
    video_files = [f for f in all_files if f.endswith(('.mp4', '.avi', '.mov', '.webm'))]
    validate_vedio_files(video_files)
    upload_folder_to_drive.main()


if __name__ == "__main__":
    main(1)
