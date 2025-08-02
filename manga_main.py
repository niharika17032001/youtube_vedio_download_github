import os
from time import sleep

import download_folder_from_drive
import ImportantVariables as imp
import upload_folder_to_drive
import youtube_video_download_and_upload_to_drive
from video_download import download_videos_from_json
from youtube_video_download_and_upload_to_drive import attempt_video_download, validate_vedio_files


def main(max_videos):
    imp_json_files_folder_id=imp.manga_imp_json_files_folder_id
    link_of_youtube_videos_json_file = imp.manga_link_of_youtube_videos_json_file
    downloaded_videos_folder = imp.downloaded_videos_folder
    metadata_file_json_file = imp.manga_metadata_file_json_file
    video_directory = downloaded_videos_folder

    download_folder_from_drive.download_folder(imp_json_files_folder_id)
    download_videos_from_json(link_of_youtube_videos_json_file, downloaded_videos_folder, metadata_file_json_file,max_videos)


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
    upload_folder_to_drive.manga_main()


if __name__ == "__main__":
    main(1)
