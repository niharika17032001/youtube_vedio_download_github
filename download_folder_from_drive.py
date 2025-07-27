import gdown

import ImportantVariables as imp_vals

def download_file_from_drive(file_id, output_path=None):
    """
    Downloads a single file from Google Drive using its file ID.

    Parameters:
    - file_id (str): The ID of the Google Drive file.
    - output_path (str, optional): The local path where the file will be saved. If None, it uses the file name from Google Drive.
    """
    url = f"https://drive.google.com/uc?id={file_id}"
    downloaded_file_path = gdown.download(url, output=output_path, quiet=False, use_cookies=False)
    print("File saved to:", downloaded_file_path)
    return downloaded_file_path

def download_folder(YOUR_FOLDER_ID):
    # Replace with your shared folder link
    shared_folder_url = f"https://drive.google.com/drive/folders/{YOUR_FOLDER_ID}?usp=sharing"

    # Use gdown to download the entire folder
    downloaded_folder_path=gdown.download_folder(shared_folder_url, quiet=False, use_cookies=False)
    print("Folder downloaded successfully to:", downloaded_folder_path)
    return downloaded_folder_path

def main():
    # drive_file_structure_file_id=imp_vals.drive_file_structure_file_id
    # download_folder(drive_file_structure_file_id)
    # print("drive_file_structure_file_id is downloaded")

    imp_json_files_folder_id=imp_vals.imp_json_files_folder_id
    download_folder(imp_json_files_folder_id)
    print("imp_json_files_folder_id is downloaded")



if __name__ == "__main__":
    main()
