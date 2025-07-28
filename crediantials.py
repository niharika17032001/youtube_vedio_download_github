import json
import os

from ImportantVariables import TOKENS_LOCAL_FILE_PATH

try:
    with open(TOKENS_LOCAL_FILE_PATH, "r") as f:
        existing_data = json.load(f)
    print("📖 Existing token file loaded.")
except json.JSONDecodeError:
    print("⚠️ Existing token file is not valid JSON. Overwriting it.")
except Exception as e:
    print(f"⚠️ Error reading existing file: {e}")

GOOGLE_YOUTUBE_CLIENT_ID = existing_data["youtube"]["client_id"]
GOOGLE_YOUTUBE_CLIENT_SECRET = existing_data["youtube"]["client_secret"]
GOOGLE_YOUTUBE_REFRESH_TOKEN = existing_data["youtube"]["refresh_token"]

GOOGLE_DRIVE_CLIENT_ID = existing_data["drive"]["client_id"]
GOOGLE_DRIVE_CLIENT_SECRET = existing_data["drive"]["client_secret"]
GOOGLE_DRIVE_REFRESH_TOKEN = existing_data["drive"]["refresh_token"]

file_path = os.path.abspath(__file__)
current_Folder_Path = os.path.dirname(file_path)
root_folder = os.path.dirname(current_Folder_Path)

print(f"Current Folder Path: {current_Folder_Path}")
print(f"Root Folder Path: {root_folder}")
screenshot_path = current_Folder_Path + '/reports/screenshot.png'
page_content_path = current_Folder_Path + '/reports/page_content.html'
video_path = current_Folder_Path + '/reports'

required_secrets = {
    "GOOGLE_YOUTUBE_CLIENT_ID": GOOGLE_YOUTUBE_CLIENT_ID,
    "GOOGLE_YOUTUBE_CLIENT_SECRET": GOOGLE_YOUTUBE_CLIENT_SECRET,
    "GOOGLE_YOUTUBE_REFRESH_TOKEN": GOOGLE_YOUTUBE_REFRESH_TOKEN,
    "GOOGLE_DRIVE_CLIENT_ID": GOOGLE_DRIVE_CLIENT_ID,
    "GOOGLE_DRIVE_CLIENT_SECRET": GOOGLE_DRIVE_CLIENT_SECRET,
    "GOOGLE_DRIVE_REFRESH_TOKEN": GOOGLE_DRIVE_REFRESH_TOKEN,
}

for key, value in required_secrets.items():
    if not value:
        raise ValueError(f"{key} is missing. Ensure it is set in GitHub Secrets.")
