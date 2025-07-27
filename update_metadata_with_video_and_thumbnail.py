import json

import ImportantVariables


def update_metadata_with_video_and_thumbnail(json_file = 'uploaded_files.json',metadata_file = ImportantVariables.metadata_file_json_file):
    # Load JSON data from file
    with open(json_file, 'r') as file:
        data = json.load(file)  # Use json.load to load from the file directly

    # Load metadata from file
    with open(metadata_file, 'r',encoding='utf-8') as file:
        metadata_dict = json.load(file)  # Same here for metadata

    print(metadata_dict)
    metadata=metadata_dict["video"]

    # Function to determine file type based on the extension
    def get_file_type(filename):
        if filename.endswith(".vtt"):
            return "Text"
        elif filename.endswith(".webp"):
            return "Thumbnail"
        elif filename.endswith(".mp4") or filename.endswith(".webm"):
            return "Video"
        else:
            return "Unknown"

    # Add video and thumbnail IDs to the metadata list
    for index, files in data["youtube_videos"].items():
        video_id = None
        thumbnail_id = None

        for filename, file_id in files.items():
            if filename.endswith(".mp4") or filename.endswith(".webm"):
                video_id = file_id
            elif filename.endswith(".webp"):
                thumbnail_id = file_id

        # Match metadata by index and add video and thumbnail IDs
        for item in metadata:
            if item["index"] == int(index):
                item["video_id"] = video_id
                item["thumbnail_id"] = thumbnail_id
    metadata_dict["video"]=metadata
    with open(metadata_file, 'w') as file:
        json.dump(metadata_dict, file, indent=4)  # Save the updated metadata with proper formatting

    return metadata_dict


def main(json_file = 'uploaded_files.json',metadata_file = ImportantVariables.metadata_file_json_file):

    # Call the function to update metadata
    updated_metadata = update_metadata_with_video_and_thumbnail(json_file, metadata_file)
    print(updated_metadata)

if __name__ == "__main__":
    main()