from urllib.parse import urlparse, parse_qs

def clean_youtube_url(url):
    parsed = urlparse(url)

    #youtu.be/VIDEO_ID
    if parsed.hostname == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]

    #youtube.com/watch?v=VIDEO_ID
    elif parsed.hostname in (
        "www.youtube.com",
        "youtube.com",
        "m.youtube.com",
    ):
        query = parse_qs(parsed.query)
        video_id = query.get("v", [None])[0]

    else:
        raise ValueError("Invalid Youtube URL")

    if not video_id:
        raise ValueError("Video ID Youtube tidak ditemukan")

    return f"https://www.youtube.com/watch?v={video_id}"