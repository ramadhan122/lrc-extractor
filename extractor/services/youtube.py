import os
import tempfile

import yt_dlp

def get_manual_subtitles(url):
    options = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
    }

    print("YT-DLP: mulai ambil info")
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(
            url,
            download=False
        )
    print("YT-DLP: extract selesai")

    subtitles = info.get("subtitles", {})

    return {
        "info": info,
        "languages": list(subtitles.keys()),
    }

def extract_subtitle(url, language="en"):
    with tempfile.TemporaryDirectory() as temp_dir:

        output_template = os.path.join(
            temp_dir,
            "subtitle"
        )

        options = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": False,
            "subtitleslangs": [language],
            "subtitlesformat": "vtt",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }

        print("YT-DLP: mulai ekstrak")
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(
                url, 
                download=True
                )

        subtitle_file = None
        print("YT-DLP: ekstrak selesai")

        for filename in os.listdir(temp_dir):
            if filename.endswith(".vtt"):
                subtitle_file = os.path.join(
                    temp_dir,
                    filename
                )
                break

        if not subtitle_file:
            return {
                "info": info,
                "source": None,
                "content": None,
            }

        with open(
            subtitle_file,
            "r",
            encoding="utf-8"
        ) as file:
            content = file.read()

        return {
            "info": info,
            "source": "manual",
            "content": content,
        }