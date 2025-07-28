import requests

import github_crediantials


def main():
    # === Configuration ===
    GITHUB_TOKEN = github_crediantials.GITHUB_TOKEN  # 🔐 Replace with your actual token
    USERNAME = "niharika17032001"
    REPO = "All_crediantial_files"
    FILE_PATH = "tokens.json"
    BRANCH = "main"
    SAVE_AS = "tokens.json"  # Local filename

    # === Build API URL ===
    url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{FILE_PATH}?ref={BRANCH}"

    # === Headers for Auth ===
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.raw"
    }

    # === Download File ===
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open(SAVE_AS, 'wb') as f:
            f.write(response.content)
        print(f"✅ File downloaded and saved as '{SAVE_AS}'")
    else:
        print(f"❌ Failed to download file: {response.status_code} - {response.text}")


if __name__ == "__main__":
    main()
