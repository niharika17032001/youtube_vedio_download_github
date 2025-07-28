import youtube_video_download_and_upload_to_drive


def main(name,index):
    if name == "amit12345":
        return youtube_video_download_and_upload_to_drive.main(index)
    else:
        return "Hello " + name + "!!"


if __name__ == "__main__":
    main("amit12345",3)
    # main(name="Amit",index=1)
