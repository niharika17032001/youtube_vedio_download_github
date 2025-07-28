import json
import os

from dotenv import load_dotenv

from ImportantVariables import TOKENS_LOCAL_FILE_PATH

load_dotenv()

try:
    with open(TOKENS_LOCAL_FILE_PATH, "r") as f:
        existing_data = json.load(f)
    print("📖 Existing token file loaded.")
except json.JSONDecodeError:
    print("⚠️ Existing token file is not valid JSON. Overwriting it.")
except Exception as e:
    print(f"⚠️ Error reading existing file: {e}")

GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")

required_secrets = {
    "GITHUB_TOKEN": GITHUB_TOKEN
}

for key, value in required_secrets.items():
    if not value:
        raise ValueError(f"{key} is missing. Ensure it is set in GitHub Secrets.")
