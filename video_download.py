import json
import os
import re

import requests
import yt_dlp
from pytube import YouTube
from tqdm import tqdm

import ImportantVariables as Imp_val
import get_video_links_from_channel
import yt_dlp_file


def remove_urls(text):
    # Regular expression to match URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    # Replace URLs with an empty string
    cleaned_text = re.sub(url_pattern, '', text)

    return cleaned_text


def clean_filename(filename):
    # Remove characters that are not allowed in filenames
    forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '⧸']
    cleaned_filename = ''.join(c for c in filename if c not in forbidden_chars)
    return cleaned_filename


def download_video(video_url, save_path, metadata_list, index):
    try:
        yt = YouTube(video_url)
        try:
            yt_dlp.download_video(video_url, save_path, metadata_list, index)
            # print(f"Downloaded video: {yt.title} ({os.path.getsize(video_file) / (1024 * 1024):.2f} MB)")
        except:
            thumbnail_url = yt.thumbnail_url
            response = requests.get(thumbnail_url)
            cleaned_title = clean_filename(yt.title)
            thumbnail_path = os.path.join(save_path, f"{cleaned_title}.jpg")
            with open(thumbnail_path, "wb") as img_file:
                img_file.write(response.content)
            video = yt.streams.get_highest_resolution()
            video_file = video.download(output_path=save_path)
            cleaned_description = remove_urls(yt.description)
            # Store video metadata in a dictionary
            video_metadata = {
                "title": cleaned_title,
                "tags": yt.keywords,
                "description": cleaned_description
            }

            metadata_list.append(video_metadata)

            print(f"Downloaded video: {yt.title} ({os.path.getsize(video_file) / (1024 * 1024):.2f} MB)")

    except Exception as e:
        print("Error downloading video:", e)


def get_channel_id(video_links, link_of_youtube_videos_json_file):
    if len(video_links) < 1:
        video_links= get_video_links_from_channel.main()
        # with open(link_of_youtube_videos_json_file, "r") as file:
        #     video_links = json.load(file)

    return video_links


def save_link_of_youtube_videos_json_file(link_of_youtube_videos_json_file, video_links, data):
    # data["playlists"].setdefault(channel_name, {})
    # data["playlists"][channel_name].setdefault(playlist_title, [])
    # data["playlists"][channel_name][playlist_title].extend(video_links)
    data["video"] = video_links
    with open(link_of_youtube_videos_json_file, "w") as json_file:
        json.dump(data, json_file, indent=4)


def convert_imp_json_to_dic_from_list(data):
    if isinstance(data, list):
        data = {
            "video": data,
            "shorts": [],
            "playlists": {}
        }
    return data


def save_metadata_file_json_file(metadata_file_json_file, metadata_list, metadata):
    metadata["video"].extend(metadata_list)
    with open(metadata_file_json_file, "w", encoding="utf-8") as json_file:
        json.dump(metadata, json_file, indent=4)


def download_videos_from_json(link_of_youtube_videos_json_file, downloaded_videos_folder, metadata_file_json_file,
                              max_videos=5,start_index = -1,end_index = -1):
    with open(link_of_youtube_videos_json_file, "r") as file:
        data = json.load(file)
    data = convert_imp_json_to_dic_from_list(data)
    with open(metadata_file_json_file, "r", encoding="utf-8") as file:
        metadata = json.load(file)
    metadata = convert_imp_json_to_dic_from_list(metadata)

    video_links = data["video"]
    print("Total videos to be downloaded: ", len(video_links))

    video_links = get_channel_id(video_links, link_of_youtube_videos_json_file)

    if not os.path.exists(downloaded_videos_folder):
        os.makedirs(downloaded_videos_folder)

    metadata_list = []

    if max_videos < 0:
        max_videos = len(video_links)
    if start_index < 0:
        index_set = {video['index'] for video in metadata['video']}
        if len(index_set)==0:
            max_index= -1
        else:
            max_index  = max(index_set)
        start_index = max_index +1
        print("start index:", start_index)
    if end_index < 0:
        end_index = start_index +max_videos


    # Apply max_videos limit
    selected_videos = video_links[:max_videos]
    main_index=start_index

    # your download logic here

    try:
        for index, video_url in tqdm(
                enumerate(selected_videos, start=start_index),
                desc="Downloading Videos",
                total=len(selected_videos)
        ):
            # download_video(video_url, downloaded_videos_folder, metadata_list, index)
            yt_dlp_file.download_video(video_url, downloaded_videos_folder, metadata_list, index)
            main_index = index


    except yt_dlp.utils.DownloadError as e:
        print(f"Download failed: {e}")

    save_link_of_youtube_videos_json_file(link_of_youtube_videos_json_file, video_links[main_index + 1:], data)
    save_metadata_file_json_file(metadata_file_json_file, metadata_list, metadata)


def main(max_videos=5):
    link_of_youtube_videos_json_file = Imp_val.link_of_youtube_videos_json_file
    downloaded_videos_folder = Imp_val.downloaded_videos_folder
    metadata_file_json_file = Imp_val.metadata_file_json_file

    download_videos_from_json(link_of_youtube_videos_json_file, downloaded_videos_folder, metadata_file_json_file,
                              max_videos)


if __name__ == "__main__":
    main(1)
