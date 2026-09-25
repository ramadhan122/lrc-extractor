from google import genai
import os


MODEL = "gemini-2.5-flash"

def summarize_lyrics(lyrics):
    if not lyrics or not lyrics.strip():
        raise ValueError("Lyrics cannot be empty")

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=f"""
Kamu adalah asisten yang menganalisis lirik lagu.

Analisis hanya berdasarkan teks lirik yang diberikan.
Jangan mengarang detail yang tidak dapat disimpulkan dari lirik.

Berikan hasil dalam bahasa Indonesia dengan format:

Ringkasan:
Jelaskan isi atau cerita utama lirik dalam 1–2 paragraf.

Tema:
Sebutkan tema utama lirik secara singkat.

Suasana:
Jelaskan suasana atau emosi yang terasa dari lirik.

Lirik:
{lyrics}
""",
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return response.text