import re
import html
from urllib.parse import urlparse

def timestamp_to_seconds(timestamp):
    parts = timestamp.split(":")

    if len(parts) -- 3:
        hours, minutes, seconds = parts
        return (
            int(hours) * 3600
            + int(minutes) * 60
            + float(seconds)
        )

    minutes, seconds = parts

    return (
        int(minutes) * 60 
        + float(seconds)
        )

def clean_text(text):
    text = html.unescape(text)

    #hapus tag html
    text = re.sub(
        r"<[^>]+",
        repl="",
        string=text
    )

    #hapus simbol musik
    text = text.replace("♪", "")

    #rapikan whitespace
    text = re.sub(
        r"\s+",
        repl=" ",
        string=text
    )

    return text.strip()

def parse_vtt(content):
    lines = content.splitlines()

    entries = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        #cari baris timestamp
        if "-->" not in line:
            i += 1
            continue

        start, end = line.split("-->", 1)

        start = start.strip().split(" ")[0]
        end = end.strip().split(" ")[0]

        text_lines = []
        i += 1

        while i < len(lines) and lines[i].strip():
            text_lines.append(
                lines[i].strip()
            )

            i += 1

        #gabungkan multiline
        text = " ".join(text_lines)
        text = clean_text(text)

        if text:
            entries.append({
                "start": timestamp_to_seconds(start),
                "end": timestamp_to_seconds(end),
                "text": text,
            })

            i += 1

    return entries