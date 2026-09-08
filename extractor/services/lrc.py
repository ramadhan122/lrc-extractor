def format_lrc_timestamp(seconds):
    minutes = int(seconds // 60)
    remaining = seconds % 60

    return f"[{minutes:02d}:{remaining:05.2f}]"

def generate_lrc(lyrics):
    lines = []

    for item in lyrics:
        timestamp = format_lrc_timestamp(
            item["start"]
        )

        text = item["text"]

        lines.append(
            f"{timestamp}{text}"
        )

    return "\n".join(lines)