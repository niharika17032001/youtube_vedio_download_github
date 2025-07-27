import json
import os
import shutil

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import ImportantVariables as imp_val
import crediantials

# Replace with your actual credentials
CLIENT_ID = crediantials.GOOGLE_DRIVE_CLIENT_ID
CLIENT_SECRET = crediantials.GOOGLE_DRIVE_CLIENT_SECRET
REFRESH_TOKEN = crediantials.GOOGLE_DRIVE_REFRESH_TOKEN

# Construct credentials object
credentials = Credentials(
    token=None,  # Not used with refresh token
    refresh_token=REFRESH_TOKEN,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    token_uri='https://oauth2.googleapis.com/token',
)

# Build the Drive API service
drive_service = build('drive', 'v3', credentials=credentials)




def list_all_folders_in_drive(folder_id=None, output_json_path="drive_folders.json"):
    """
    Lists all folders in Google Drive (or within a specific folder) and saves them to a JSON file.

    Args:
        folder_id (str, optional): If provided, list only folders in this folder.
        output_json_path (str): Path to the output JSON file.
    """
    # MIME type for folders
    query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if folder_id:
        query += f" and '{folder_id}' in parents"

    all_main_folders = []
    page_token = None

    while True:
        response = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=page_token
        ).execute()

        for folder in response.get('files', []):
            folder_info = {
                'name': folder.get('name'),
                'id': folder.get('id')
            }
            all_main_folders.append(folder_info)

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break


    # Save to JSON file
    with open(output_json_path, 'w') as f:
        json.dump(all_main_folders, f, indent=4)

    print(f"Saved {len(all_main_folders)} folders to {output_json_path}")


def build_folder_tree(folder_id, drive_service):
    """
    Builds a hierarchical folder structure starting from a given folder ID.

    Args:
        folder_id (str): Root folder ID.
        drive_service: Google Drive API service.

    Returns:
        dict: Folder tree starting from the given folder.
    """
    # Get folder name
    folder = drive_service.files().get(fileId=folder_id, fields='name').execute()
    folder_name = folder.get('name', 'Unknown')

    folder_tree = {
        "name": folder_name,
        "id": folder_id,
        "children": []
    }

    # Query subfolders
    query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    page_token = None

    while True:
        response = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=page_token
        ).execute()

        subfolders = response.get('files', [])
        for subfolder in subfolders:
            subfolder_tree = build_folder_tree(subfolder['id'], drive_service)
            folder_tree['children'].append(subfolder_tree)

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    return folder_tree



def build_folder_and_files_tree(service, root_folder_id, root_folder_name):
    """
    Build the folder structure starting from the root_folder_id.
    """
    return {
        "name": root_folder_name,
        "id": root_folder_id,
        "children": get_children(service, root_folder_id)
    }

def get_drive_service():
    """
    Authenticate and return a Google Drive service object.
    """
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri='https://oauth2.googleapis.com/token',
    )
    return build('drive', 'v3', credentials=creds)


def is_folder(file):
    """Return True if the file is a folder."""
    return file.get('mimeType') == 'application/vnd.google-apps.folder'


def get_children(service, folder_id):
    """
    Recursively get all children (files and subfolders) of a folder.
    """
    children = []

    query = f"'{folder_id}' in parents and trashed = false"
    page_token = None

    while True:
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=page_token
        ).execute()

        for file in response.get('files', []):
            child = {
                "name": file['name'],
                "id": file['id']
            }

            if is_folder(file):
                child["children"] = get_children(service, file['id'])
            else:
                child["children"] = []  # Optional: include or exclude files

            children.append(child)

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return children





def save_folder_tree_to_json(root_folder_id, output_path=imp_val.drive_file_structure_file):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Your root folder
    folder_id = imp_val.youtube_vedio_folder_id
    folder_name = "youtube_videos"  # You can fetch dynamically if needed

    folder_tree = build_folder_and_files_tree(drive_service, folder_id, folder_name)
    with open(output_path, 'w') as f:
        json.dump(folder_tree, f, indent=4)
    print(f"Saved folder tree to {output_path}")
    return output_path


if __name__ == "__main__":
    # list_all_folders_in_drive(folder_id=imp_val.youtube_videos_for_upload_folder_id)
    # Root folder: youtube_videos
    # youtube_videos_folder_id = "1vsBjK-7SBeJAwNv5CeBNBT_hiHWu_6pM"
    youtube_videos_folder_id = imp_val.youtube_videos_for_upload_folder_id
    save_folder_tree_to_json(youtube_videos_folder_id)

