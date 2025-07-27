from dotenv import load_dotenv
import os

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GOOGLE_DRIVE_CLIENT_ID = os.getenv("GOOGLE_DRIVE_CLIENT_ID")
GOOGLE_DRIVE_CLIENT_SECRET = os.getenv("GOOGLE_DRIVE_CLIENT_SECRET")
GOOGLE_DRIVE_REFRESH_TOKEN = os.getenv("GOOGLE_DRIVE_REFRESH_TOKEN")


if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY key is missing. Ensure it is set in GitHub Secrets.")

if not GOOGLE_DRIVE_CLIENT_ID:
    raise ValueError("GOOGLE_DRIVE_CLIENT_ID key is missing. Ensure it is set in GitHub Secrets.")

if not GOOGLE_DRIVE_CLIENT_SECRET:
    raise ValueError("GOOGLE_DRIVE_CLIENT_SECRET key is missing. Ensure it is set in GitHub Secrets.")

if not GOOGLE_DRIVE_REFRESH_TOKEN:
    raise ValueError("GOOGLE_DRIVE_REFRESH_TOKEN key is missing. Ensure it is set in GitHub Secrets.")
