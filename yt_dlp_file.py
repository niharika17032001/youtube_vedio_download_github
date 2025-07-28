import os
import re
import shutil
import requests
import yt_dlp

import ImportantVariables as imp

cookies_file_path = imp.cookies_file_path


def remove_urls(text):
    return re.sub(r'http[s]?://\S+', '', text)


def clean_filename(filename):
    forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '⧸']
    return ''.join(c for c in filename if c not in forbidden_chars)


def copy_file(old_file_path, new_file_path):
    try:
        shutil.copy2(old_file_path, new_file_path)
        print(f"✅ File copied from '{old_file_path}' to '{new_file_path}'")
    except Exception as e:
        print(f"❌ File copy error: {e}")


def create_temp_cookies_file(main_cookies_file):
    copy_file(main_cookies_file, "cookies.txt")
    return "cookies.txt"


def save_caption_manually(auto_captions, lang, save_path, index):
    if lang in auto_captions:
        for entry in auto_captions[lang]:
            ext = entry.get('ext')
            caption_url = entry.get('url')
            print(f"🌐 Trying to download: {ext} → {caption_url}")

            try:
                response = requests.get(caption_url)
                if response.status_code == 200 and len(response.content) > 100:
                    caption_path = os.path.join(save_path, f"vedio_{index}.{lang}.{ext}")
                    with open(caption_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ Captions saved manually to: {caption_path}")
                    return True
                else:
                    print(f"⚠️ Caption {ext} is empty or invalid (len={len(response.content)})")

            except Exception as e:
                print(f"❌ Failed downloading {ext} captions: {e}")

    print("⚠️ No working caption format found.")
    return False


def download_video(video_url, save_path, metadata_list, index):
    save_path = os.path.join(save_path, f"{index}")
    os.makedirs(save_path, exist_ok=True)

    cookies_file = create_temp_cookies_file(cookies_file_path)

    # Step 1: Probe metadata
    probe_opts = {
        'quiet': True,
        'cookiefile': cookies_file,
    }

    with yt_dlp.YoutubeDL(probe_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

    subtitles = info.get("subtitles", {})
    auto_captions = info.get("automatic_captions", {})
    thumbnail_url = info.get("thumbnail")

    preferred_langs = []
    for lang in ['hi', 'en']:
        if lang in subtitles or lang in auto_captions:
            preferred_langs.append(lang)

    print("🔤 Subtitles:", list(subtitles.keys()))
    print("🧠 Auto-captions:", list(auto_captions.keys()))

    # Step 2: Download video, auto captions, and thumbnail
    ydl_opts = {
        'outtmpl': os.path.join(save_path, f'vedio_{index}.%(ext)s'),
        'writesubtitles': False,
        'writeautomaticsub': True,
        'writeinfojson': True,
        'writethumbnail': True,
        'subtitleslangs': preferred_langs,
        'subtitlesformat': 'vtt',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'cookiefile': cookies_file
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
    except Exception as e:
        print(f"❌ yt-dlp download failed: {e}")
        return

    # Step 3: Manually save captions if not auto-saved
    caption_saved = False
    for lang in preferred_langs:
        found = any(f"vedio_{index}.{lang}.vtt" in f for f in os.listdir(save_path))
        if not found:
            caption_saved = save_caption_manually(auto_captions, lang, save_path, index)

    # Step 4: Save thumbnail (if not already downloaded)
    if thumbnail_url:
        try:
            import requests
            thumb_path = os.path.join(save_path, f'vedio_{index}.webp')
            r = requests.get(thumbnail_url, timeout=10)
            with open(thumb_path, 'wb') as f:
                f.write(r.content)
            print(f"🖼️ Thumbnail saved to: {thumb_path}")
        except Exception as e:
            print(f"⚠️ Failed to save thumbnail manually: {e}")

    # Step 5: Save metadata
    cleaned_title = clean_filename(info.get("title", f"video_{index}"))
    cleaned_description = remove_urls(info.get("description", ""))

    video_metadata = {
        "index": index,
        "title": cleaned_title,
        "tags": info.get('tags', []),
        "description": cleaned_description,
        "age_restricted": info.get('age_limit', 0) > 0,
        "age_limit": info.get('age_limit', 0),
    }
    metadata_list.append(video_metadata)

    ext = info.get("ext", "mp4")
    print(f"✅ Downloaded: {cleaned_title}")
    print(f"📁 Saved: vedio_{index}.{ext}")
    if caption_saved:
        print("📑 Captions saved manually.")
    else:
        print("⚠️ Captions not found or saved.")

def temp_main(video_url):
    metadata = []
    download_video(video_url, "downloaded_videos", metadata, 1)
    print("\n📝 Metadata:", metadata)


if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=zr0lhEo26zc"
    temp_main(video_url)
