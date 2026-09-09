import os
import tempfile

import yt_dlp


def extract_subtitle_data(url, language=None):

    # =========================
    # STEP 1
    # Ambil metadata + daftar subtitle
    # =========================

    info_options = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(info_options) as ydl:

        print("YT-DLP: mengambil informasi video")

        info = ydl.extract_info(
            url,
            download=False
        )

        print("YT-DLP: informasi video selesai")

    subtitles = info.get("subtitles", {})
    manual_languages = list(subtitles.keys())

    print("Manual captions:", manual_languages)

    if not manual_languages:
        return {
            "info": info,
            "manual_languages": [],
            "language": None,
            "content": None,
            "source": None,
        }

    # =========================
    # STEP 2
    # Pilih bahasa
    # =========================

    if not language:

        english_language = next(
            (
                lang
                for lang in manual_languages
                if lang == "en" or lang.startswith("en-")
            ),
            None
            )

        if english_language:
            language = english_language
        else:
            language = manual_languages[0]

    elif language not in manual_languages:

        raise ValueError(
            f"Manual subtitle '{language}' ga ada cuy"
        )

    print("Selected language:", language)

    # =========================
    # STEP 3
    # Download subtitle
    # =========================

    with tempfile.TemporaryDirectory() as temp_dir:

        output_template = os.path.join(
            temp_dir,
            "subtitle"
        )

        subtitle_options = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": False,
            "subtitleslangs": [language],
            "subtitlesformat": "vtt",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(subtitle_options) as ydl:

            print("YT-DLP: mulai download subtitle")

            ydl.extract_info(
                url,
                download=True
            )

            print("YT-DLP: subtitle selesai didownload")

        subtitle_file = None

        for filename in os.listdir(temp_dir):

            if filename.endswith(".vtt"):
                subtitle_file = os.path.join(
                    temp_dir,
                    filename
                )
                break

        content = None

        if subtitle_file:

            with open(
                subtitle_file,
                "r",
                encoding="utf-8"
            ) as file:
                content = file.read()

        return {
            "info": info,
            "manual_languages": manual_languages,
            "language": language,
            "content": content,
            "source": "manual" if content else None,
        }

def select_language(manual_languages, requested_language=None):
    if requested_language:
        if requested_language not in manual_languages:
            raise ValueError(
                f"Manual subtitle '{requested_language}' not found"
            )
        return requested_language

    english_language = next(
        (
            lang
            for lang in manual_languages
            if lang == "en" or lang.startswith("en-")
        ),
        None
        )

    if english_language:
        return english_language

    return manual_languages[0]

def get_manual_subtitles(url):

    print("=== START YT-DLP ===")

    options = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 15,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            url,
            download=False
        )

    subtitles = info.get("subtitles", {})

    return {
        "info": info,
        "manual_languages": list(subtitles.keys()),
    }