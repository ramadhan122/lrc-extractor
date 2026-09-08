import os
import tempfile

import yt_dlp


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

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(
                url, 
                download=True
                )

        subtitle_file = None

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