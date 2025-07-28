import json
import re
from urllib.parse import urlparse

from yt_dlp import YoutubeDL

import ImportantVariables as Imp_val
import yt_dlp_file

cookies_file_path = Imp_val.cookies_file_path


def validate_url(channel_input):
    channel_input = channel_input.strip()

    # If full YouTube URL
    if channel_input.startswith("https://www.youtube.com/"):
        parsed = urlparse(channel_input)
        path_parts = parsed.path.strip("/").split("/")

        # Keep only the first part (e.g., '@handle' or 'channel/UC...')
        if path_parts[0].startswith("@"):
            return f"https://www.youtube.com/{path_parts[0]}"
        elif path_parts[0] == "channel" and len(path_parts) > 1:
            return f"https://www.youtube.com/channel/{path_parts[1]}"
        elif path_parts[0] == "c" and len(path_parts) > 1:
            return f"https://www.youtube.com/c/{path_parts[1]}"
        elif path_parts[0] == "user" and len(path_parts) > 1:
            return f"https://www.youtube.com/user/{path_parts[1]}"
        else:
            return "https://www.youtube.com/" + path_parts[0]

    # If it's a channel ID (starts with UC)
    if re.fullmatch(r'UC[\w-]{22,}', channel_input):
        return f"https://www.youtube.com/channel/{channel_input}"

    # If it's a handle like @name
    if channel_input.startswith("@"):
        return f"https://www.youtube.com/{channel_input}"

    # Assume it's a custom name
    return f"https://www.youtube.com/c/{channel_input}"


def get_channel_url():
    channels_list_json_file = Imp_val.channels_list_json_file

    with open(channels_list_json_file, "r") as file:
        channel_url_list = json.load(file)

    print("total channel in the list :", len(channel_url_list))
    channel_url = channel_url_list.pop(0)

    print("channel_url :", channel_url)

    with open(channels_list_json_file, "w") as f:
        json.dump(channel_url_list, f, indent=4)

    channel_url = validate_url(channel_url)

    return channel_url


def get_video_links_from_channel(channel_url):
    ydl_opts = {'quiet': True, 'extract_flat': True,  # Get only metadata, not full video info
        'skip_download': True}

    video_urls = []

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(channel_url, download=False)
        if 'entries' in info_dict:
            for entry in info_dict['entries']:
                video_urls.append(f"https://www.youtube.com/watch?v={entry['id']}")

    return video_urls


def create_temp_cookies_file(main_cookies_file):
    yt_dlp_file.copy_file(main_cookies_file, "cookies.txt")
    return "cookies.txt"


def get_info_dict(channel_url, output_json_path="channel_info.json"):
    cookies_file = create_temp_cookies_file(cookies_file_path)
    ydl_opts = {'quiet': True, 'extract_flat': True,  # Only metadata (not full video info)
        'skip_download': True, 'cookiefile': cookies_file}

    video_urls = []

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(channel_url, download=False)

        # Save info_dict to a JSON file
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(info_dict, f, indent=4, ensure_ascii=False)

        # Extract video URLs
        if 'entries' in info_dict:
            for entry in info_dict['entries']:
                video_urls.append(f"https://www.youtube.com/watch?v={entry['id']}")

    return video_urls


def main():
    link_of_youtube_videos_json_file = Imp_val.link_of_youtube_videos_json_file

    # Example usage
    # channel_link = 'https://www.youtube.com/@CHANNEL_NAME/videos'  # or https://www.youtube.com/c/CHANNEL_NAME or /user/...
    # channel_link = 'https://www.youtube.com/@tipsofficial/videos'  # or https://www.youtube.com/c/CHANNEL_NAME or /user/...
    # channel_link = 'https://www.youtube.com/@nftartist8494/videos'
    # channel_link = 'https://www.youtube.com/channel/UCOSXCgrHZt39Bw3T5YMVLmg/videos'
    channel_url = get_channel_url()
    channel_videos_link = f'{channel_url}/videos'
    print("channel_videos_link : ", channel_videos_link)

    video_links = get_info_dict(channel_videos_link)
    print(len(video_links))
    with open(link_of_youtube_videos_json_file, "w") as f:
        json.dump(video_links, f, indent=4)

    # Print the result
    # for link in video_links:
    #     print(link)
    return video_links


if __name__ == "__main__":
    main()
