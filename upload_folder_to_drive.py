import json
import os
import shutil

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import ImportantVariables as imp_val
import crediantials
import update_metadata_with_video_and_thumbnail

# Replace with your actual credentials
CLIENT_ID = crediantials.GOOGLE_DRIVE_CLIENT_ID
CLIENT_SECRET = crediantials.GOOGLE_DRIVE_CLIENT_SECRET
REFRESH_TOKEN = crediantials.GOOGLE_DRIVE_REFRESH_TOKEN

# Construct credentials object
credentials = Credentials(token=None,  # Not used with refresh token
                          refresh_token=REFRESH_TOKEN, client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                          token_uri='https://oauth2.googleapis.com/token', )

# Build the Drive API service
drive_service = build('drive', 'v3', credentials=credentials)


def get_existing_file_id(filename, parent_drive_folder_id):
    """Checks if a file with the given name exists in the specified Google Drive folder."""
    query = f"name = '{filename}' and '{parent_drive_folder_id}' in parents and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])
    return files[0]['id'] if files else None


def list_all_files_in_drive(folder_id=None, output_json_path="drive_files.json"):
    """
    Lists all files in Google Drive (or a folder) and saves them to a JSON file.

    Args:
        folder_id (str, optional): If provided, list only files in this folder.
        output_json_path (str): Path to the output JSON file.
    """
    query = "trashed = false"
    if folder_id:
        query += f" and '{folder_id}' in parents"

    all_files = []
    page_token = None

    while True:
        response = drive_service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()

        for file in response.get('files', []):
            file_info = {'name': file.get('name'), 'id': file.get('id')}
            all_files.append(file_info)

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    # Save to JSON file
    with open(output_json_path, 'w') as f:
        json.dump(all_files, f, indent=4)

    print(f"Saved {len(all_files)} files to {output_json_path}")


def get_or_create_folder(folder_name, parent_drive_folder_id):
    """Checks if a folder exists in Google Drive, creates it if not, and returns its ID."""
    query = f"name = '{folder_name}' and '{parent_drive_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])

    if files:
        return files[0]['id']

    file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder',
                     'parents': [parent_drive_folder_id]}
    folder = drive_service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')


def upload_file_to_drive(file_path, parent_drive_folder_id):
    """
    Uploads a single file to a specified Google Drive folder, overriding if it already exists.

    Args:
        file_path (str): Full path to the file.
        parent_drive_folder_id (str): Google Drive folder ID to upload into.
    """
    if not os.path.isfile(file_path):
        print("Error: File does not exist.")
        return

    filename = os.path.basename(file_path)
    print(f"Uploading: {filename}...")

    # Check if file already exists in the target Drive folder
    existing_file_id = get_existing_file_id(filename, parent_drive_folder_id)
    if existing_file_id:
        print(f"File {filename} already exists. Overriding...")
        drive_service.files().delete(fileId=existing_file_id).execute()

    # Prepare upload metadata
    file_metadata = {'name': filename, 'parents': [parent_drive_folder_id]}

    media = MediaFileUpload(file_path, resumable=True)

    # Upload file
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    print(f"Uploaded {filename}, File ID: {uploaded_file.get('id')}")


def upload_folder_to_drive(local_folder_path, parent_drive_folder_id):
    """Uploads all files and subfolders from a local folder to a specified folder in Google Drive, overriding existing files."""
    if not os.path.exists(local_folder_path):
        print("Error: Folder does not exist.")
        return

    for item in os.listdir(local_folder_path):
        item_path = os.path.join(local_folder_path, item)

        if os.path.isdir(item_path):  # Handle subfolders
            subfolder_id = get_or_create_folder(item, parent_drive_folder_id)
            upload_folder_to_drive(item_path, subfolder_id)
        elif os.path.isfile(item_path):  # Handle files
            print(f"Uploading: {item}...")
            existing_file_id = get_existing_file_id(item, parent_drive_folder_id)

            if existing_file_id:
                print(f"File {item} already exists. Overriding...")
                drive_service.files().delete(fileId=existing_file_id).execute()

            file_metadata = {'name': item, 'parents': [parent_drive_folder_id]}
            media = MediaFileUpload(item_path, resumable=True)
            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            print(f"Uploaded {item}, File ID: {file.get('id')}")


def upload_youtube_folder_to_drive(local_folder_path, parent_drive_folder_id, output_json_path="uploaded_files.json",
                                   uploaded_files=None, folder_stack=None, ):
    # Load or create JSON metadata once
    if uploaded_files is None:
        if os.path.exists(output_json_path):
            with open(output_json_path, "r") as f:
                uploaded_files = json.load(f)
        else:
            uploaded_files = {}

    if folder_stack is None:
        folder_stack = []

    # Navigate into correct nested location
    ptr = uploaded_files
    for folder in folder_stack:
        if folder not in ptr:
            ptr[folder] = {}
        ptr = ptr[folder]

    for item in os.listdir(local_folder_path):
        item_path = os.path.join(local_folder_path, item)

        if os.path.isdir(item_path):
            subfolder_id = get_or_create_folder(item, parent_drive_folder_id)
            upload_youtube_folder_to_drive(item_path, subfolder_id, output_json_path, uploaded_files=uploaded_files,
                                           folder_stack=folder_stack + [item], )

        elif os.path.isfile(item_path):
            print(f"Uploading: {item}...")
            existing_file_id = get_existing_file_id(item, parent_drive_folder_id)

            if existing_file_id:
                print(f"File {item} already exists. Overriding...")
                drive_service.files().delete(fileId=existing_file_id).execute()

            file_metadata = {'name': item, 'parents': [parent_drive_folder_id]}
            media = MediaFileUpload(item_path, resumable=True)
            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            file_id = file.get('id')
            ptr[item] = file_id
            print(f"Uploaded {item}, File ID: {file_id}")

    # Save only at the top level
    if not folder_stack:
        with open(output_json_path, "w") as f:
            json.dump(uploaded_files, f, indent=4)
        print(f"Metadata saved to {output_json_path}")


def copy_files_to_folder(files, destination_folder):
    """
    Copies a list of files to a specified folder.

    Args:
        files (list): List of file paths to copy.
        destination_folder (str): Path to the target folder.
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)  # Create the folder if it doesn't exist

    for file in files:
        if os.path.exists(file):  # Check if the file exists
            shutil.copy(file, destination_folder)
            print(f"Copied: {file} -> {destination_folder}")
        else:
            print(f"File not found: {file}")


def copy_folders_to_folder(folders, destination_folder):
    """
    Copies a list of folders to a specified folder.

    Args:
        folders (list): List of folder paths to copy.
        destination_folder (str): Path to the target folder.
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for folder in folders:
        if os.path.exists(folder) and os.path.isdir(folder):
            folder_name = os.path.basename(folder)
            target_path = os.path.join(destination_folder, folder_name)

            # Remove existing folder if already exists
            if os.path.exists(target_path):
                shutil.rmtree(target_path)

            shutil.copytree(folder, target_path)
            print(f"Copied folder: {folder} -> {target_path}")
        else:
            print(f"Folder not found or not a directory: {folder}")


def empty_drive_folder(folder_id):
    """Deletes all files inside a specified Google Drive folder."""
    query = f"'{folder_id}' in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        print("Google Drive folder is already empty.")
        return

    for file in files:
        try:
            drive_service.files().delete(fileId=file['id']).execute()
            print(f"Deleted: {file['name']}")
        except Exception as e:
            print(f"Error deleting {file['name']}: {e}")


def prepare_folder_to_upload(destination_folder):
    video_directory = imp_val.downloaded_videos_folder
    imp_json_files = [imp_val.metadata_file_json_file, imp_val.link_of_youtube_videos_json_file,
                      imp_val.channels_list_json_file]
    video_files = [os.path.join(video_directory, f) for f in os.listdir(video_directory) if
                   os.path.isfile(os.path.join(video_directory, f))]
    video_folders = [os.path.join(video_directory, f) for f in os.listdir(video_directory) if
                     os.path.isdir(os.path.join(video_directory, f))]

    all_files = imp_json_files + video_files
    youtube_vedio_folder = destination_folder + "/youtube_videos"
    imp_json_files_folder = destination_folder + "/imp_json_files"

    if not os.path.exists(youtube_vedio_folder):
        os.makedirs(youtube_vedio_folder)

    if not os.path.exists(imp_json_files_folder):
        os.makedirs(imp_json_files_folder)

    copy_files_to_folder(video_files, youtube_vedio_folder)
    # copy_folders_to_folder(video_folders,youtube_vedio_folder)
    copy_files_to_folder(imp_json_files, imp_json_files_folder)


def prepare_youtube_folder_to_upload(destination_folder):
    video_directory = imp_val.downloaded_videos_folder

    video_files = [os.path.join(video_directory, f) for f in os.listdir(video_directory) if
                   os.path.isfile(os.path.join(video_directory, f))]
    video_folders = [os.path.join(video_directory, f) for f in os.listdir(video_directory) if
                     os.path.isdir(os.path.join(video_directory, f))]

    youtube_vedio_folder = destination_folder + "/youtube_videos"

    # copy_files_to_folder(video_files, youtube_vedio_folder)
    copy_folders_to_folder(video_folders, youtube_vedio_folder)

def prepare_manga_youtube_folder_to_upload(destination_folder,video_directory = imp_val.downloaded_videos_folder):


    video_files = [os.path.join(video_directory, f) for f in os.listdir(video_directory) if
                   os.path.isfile(os.path.join(video_directory, f))]
    video_folders = [os.path.join(video_directory, f) for f in os.listdir(video_directory) if
                     os.path.isdir(os.path.join(video_directory, f))]

    youtube_vedio_folder = destination_folder

    # copy_files_to_folder(video_files, youtube_vedio_folder)
    copy_folders_to_folder(video_folders, youtube_vedio_folder)


def prepare_manga_imp_json_folder_to_upload(destination_folder,imp_json_files):

    imp_json_files_folder = destination_folder

    copy_files_to_folder(imp_json_files, imp_json_files_folder)


def prepare_imp_json_folder_to_upload(destination_folder):
    imp_json_files = [
        imp_val.metadata_file_json_file,
        imp_val.link_of_youtube_videos_json_file,
        imp_val.channels_list_json_file
    ]
    imp_json_files_folder = destination_folder + "/imp_json_files"

    copy_files_to_folder(imp_json_files, imp_json_files_folder)


def prepare_metadata_for_upload(metadata_file_json_file):
    update_metadata_with_video_and_thumbnail.main(metadata_file=metadata_file_json_file)


def manga_main():
    parent_drive_folder_id = imp_val.youtube_videos_for_upload_folder_id
    current_folder = imp_val.current_Folder_Path
    youtube_folder_to_local_path_for_upload = current_folder + "/youtube_folder_to_upload"+"/manga_youtube_videos"
    imp_json_folder_local_path_for_upload = current_folder + "/imp_json_folder_to_upload" +"/manga_imp_json_file"

    youtube_folder_to_upload_path = current_folder + "/youtube_folder_to_upload"
    imp_json_folder_to_upload_path = current_folder + "/imp_json_folder_to_upload"
    metadata_file_json_file=imp_val.manga_metadata_file_json_file
    video_directory = imp_val.downloaded_videos_folder

    manga_imp_json_files = [
        imp_val.manga_metadata_file_json_file,
        imp_val.manga_link_of_youtube_videos_json_file,
        imp_val.manga_channels_list_json_file
    ]

    # prepare_manga_youtube_folder_to_upload(youtube_folder_to_local_path_for_upload,video_directory)

    # upload_youtube_folder_to_drive(youtube_folder_to_upload_path, parent_drive_folder_id)
    # prepare_metadata_for_upload(metadata_file_json_file)

    prepare_manga_imp_json_folder_to_upload(imp_json_folder_local_path_for_upload,manga_imp_json_files)
    upload_folder_to_drive(imp_json_folder_to_upload_path, parent_drive_folder_id)



def main():
    parent_drive_folder_id = imp_val.youtube_videos_for_upload_folder_id
    current_folder = imp_val.current_Folder_Path
    youtube_folder_to_upload_path = current_folder + "/youtube_folder_to_upload"
    imp_json_folder_to_upload_path = current_folder + "/imp_json_folder_to_upload"
    metadata_file_json_file=imp_val.metadata_file_json_file

    # prepare_youtube_folder_to_upload(youtube_folder_to_upload_path)
    #
    # upload_youtube_folder_to_drive(youtube_folder_to_upload_path, parent_drive_folder_id)
    # prepare_metadata_for_upload(metadata_file_json_file)

    prepare_imp_json_folder_to_upload(imp_json_folder_to_upload_path)
    upload_folder_to_drive(imp_json_folder_to_upload_path, parent_drive_folder_id)





    # destination_drive_file_structure_folder = imp_val.create_drive_file_structure_folder()
    # prepare_folder_tree(parent_drive_folder_id,destination_drive_file_structure_folder)
    # upload_folder_to_drive(destination_drive_file_structure_folder, parent_drive_folder_id)



if __name__ == "__main__":
    main()
    # manga_main()