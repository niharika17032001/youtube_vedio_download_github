import json

import googleapiclient.discovery

import ImportantVariables as Imp_val
import crediantials


def get_channel_id():
    channels_list_json_file = Imp_val.channels_list_json_file

    with open(channels_list_json_file, "r") as file:
        channel_id_list = json.load(file)

    print("total channel in the list :", len(channel_id_list))
    channel_id = channel_id_list.pop(0)

    print("channel_id :", channel_id)

    with open(channels_list_json_file, "w") as f:
        json.dump(channel_id_list, f, indent=4)

    return channel_id


def get_channel_shorts_ids_api(channel_id, api_key):
    """Retrieves all YouTube Shorts IDs from a channel using the YouTube Data API."""

    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    shorts_ids = []
    next_page_token = None

    try:
        while True:
            request = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                type="video",
                videoDuration="short",
                maxResults=50,  # Max allowed by API.
                pageToken=next_page_token,
            )
            response = request.execute()

            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                shorts_ids.append(video_id)

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return shorts_ids

    except googleapiclient.errors.HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def main():
    api_key = crediantials.YOUTUBE_API_KEY

    channel_id = get_channel_id()
    # channel_id="UCa8lQSwGNMniXWRqmCYuTeg"

    link_of_youtube_videos_json_file = Imp_val.link_of_youtube_videos_json_file
    channel_url = f"https://www.youtube.com/channel/{channel_id}"

    shorts_ids = get_channel_shorts_ids_api(channel_id, api_key)
    shorts_urls = []
    if shorts_ids:
        print(f"Found {len(shorts_ids)} video links:")
        for url in shorts_ids:
            full_url = f"https://www.youtube.com/watch?v={url}"
            shorts_urls.append(full_url)
            print(full_url)

        with open(link_of_youtube_videos_json_file, "w") as f:
            json.dump(shorts_urls, f, indent=4)
    else:
        print("No video links found.")


if __name__ == "__main__":
    main()
