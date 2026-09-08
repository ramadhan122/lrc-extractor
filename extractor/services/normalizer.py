import re

def normalize_lyrics(lyrics):
    result = []

    previous_text = None

    for item in lyrics:
        text = item["text"].strip()

        if not text:
            continue

        #hapus cue non lirik
        if re.fullmatch(
            r"\[(music|applause|laughter|cheering|instrumental|♪+)\]",
            text,
            re.IGNORECASE
        ):
            continue

        #hilangkan duplicate berturut-turut
        if text == previous_text:
            continue

        result.append({
            "start": item["start"],
            "end": item["end"],
            "text": text,
        })

        previous_text = text

    return result