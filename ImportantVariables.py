import os

# root folder path
file_path = os.path.abspath(__file__)
current_Folder_Path = os.path.dirname(file_path)
root_folder = os.path.dirname(current_Folder_Path)

# imp folder path
content_folder = current_Folder_Path + "/content/"
downloaded_videos_folder = current_Folder_Path + "/downloaded_videos"
imp_json_files_folder = current_Folder_Path + "/imp_json_files/"
youtube_upload_folder = current_Folder_Path + "/youtube_upload_folder"
output_videos_folder = current_Folder_Path + "/output_videos"
drive_file_structure_folder = current_Folder_Path +"/folder_tree"

# imp files path
metadata_file_json_file = imp_json_files_folder + "video_metadata.json"
link_of_youtube_videos_json_file = imp_json_files_folder + "link_of_youtube_videos.json"
channels_list_json_file = imp_json_files_folder + "channels_list.json"
cookies_file_path = imp_json_files_folder + "main_cookies.txt"
drive_file_structure_file=drive_file_structure_folder+"/folder_tree.json"

# github
GITHUB_LOCAL_FILE_PATH = current_Folder_Path + "/daily_update.txt"
GITHUB_OWNER = "niharika17032001"
GITHUB_google_log_in_REPO = "google_log_in"
GITHUB_WORKFLOW_FILE = "main.yml"
GITHUB_BRANCH = "main"

# drive imp folders id
youtube_videos_for_upload_folder_id = "1V3gjZpfNJbFMPO0R1OAnrRjoqD0pozr4"
imp_json_files_folder_id = "1xjvtIZXSwpSaZS4uS0YRzhDEQuR_wgVu"
youtube_vedio_folder_id = "1vsBjK-7SBeJAwNv5CeBNBT_hiHWu_6pM"

# vedio editing paths
PATHS = {
    "logo": content_folder + "logo.png",
    "background": content_folder + "background_image.jpg",
    "banner": content_folder + "yt_banner.png",
    "subscribe": content_folder + "subscribe.png",
    "animation": content_folder + "like_share_subscribe_animation.mp4",
    "input_videos": current_Folder_Path + "input_vedio/",
    "audio": content_folder + "audio.mp3",
    "output_video": current_Folder_Path + "/output_videos/output_video_with_audio.mp4",
    "input_video_path": current_Folder_Path + "/downloaded_videos/vedio_0.webm"
}


# imp functions
def create_output_videos_folder():
    if not os.path.exists(output_videos_folder):
        os.makedirs(output_videos_folder)
    return output_videos_folder

def create_drive_file_structure_folder():
    folder=current_Folder_Path+"/drive_file_structure_folder"
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

def create_youtube_upload_folder():
    if not os.path.exists(youtube_upload_folder):
        os.makedirs(youtube_upload_folder)
    return youtube_upload_folder


def create_path_auto(path: str):
    """
    Automatically detects whether the path is a file or a folder,
    then creates all necessary directories (and an empty file if needed).

    Parameters:
    - path (str): Full path to a file or folder.
    """
    # Heuristic: if path ends with a file extension, treat it as a file
    is_file = os.path.splitext(path)[1] != ""

    dir_path = os.path.dirname(path) if is_file else path
    os.makedirs(dir_path, exist_ok=True)

    if is_file:
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write("")  # Optional: write default content
            print(f"Created file: {path}")
        else:
            print(f"File already exists: {path}")
    else:
        print(f"Created folder: {path}")


def check_paths_exist(paths):
    ignore_keys = {"input_videos", "audio", "output_video", "input_video_path"}  # Keys to ignore
    missing_paths = {}
    for key, path in paths.items():
        if key not in ignore_keys and not os.path.exists(path):
            missing_paths[key] = path

    if missing_paths:
        print("\033[91mThe following paths do not exist:\033[0m")  # Red color
        for key, path in missing_paths.items():
            print(f"\033[91m{key}: {path}\033[0m")
        raise Exception("Some required paths are missing.")
    else:
        print("All paths exist.")

    return missing_paths
