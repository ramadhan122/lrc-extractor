import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import time
import re

import hashlib
from .models import SummaryCache
from django.shortcuts import render
from .services.parser import parse_vtt
from .services.normalizer import normalize_lyrics
from .services.lrc import generate_lrc
from .services.url import clean_youtube_url
from .services.youtube import(
    extract_subtitle_data,
    get_manual_subtitles,
)
from .services.summarizer import summarize_lyrics

def home(request):
    return render(request, "extractor/index.html")

@csrf_exempt
@api_view(["POST"])
def extract_lyrics(request):

    url = request.data.get("url")

    if not url:
        return Response(
            {"error": "YouTube URL is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:

        url = clean_youtube_url(url)

        print("CLEAN URL:", url)

        language = request.data.get("language")

        print("STEP 1 - extracting subtitle")

        result = extract_subtitle_data(
            url,
            language
        )

        info = result["info"]
        manual_languages = result["manual_languages"]

        if not manual_languages:

            return Response({
                "error": "No manual captions available",
                "video_id": info.get("id"),
                "title": info.get("title"),
            })

        if not result["content"]:

            return Response({
                "error": "Subtitle could not be downloaded",
                "language": result["language"],
            })

        print("STEP 2 - subtitle extracted")

        print("STEP 3 - parsing VTT")

        lyrics = parse_vtt(
            result["content"]
        )

        print("STEP 4 - parser success")

        lyrics = normalize_lyrics(
            lyrics
        )

        print("STEP 5 - normalization success")

        lrc = generate_lrc(
            lyrics
        )

        print("STEP 6 - LRC generated")

        return Response({
            "video_id": info.get("id"),
            "title": info.get("title"),
            "source": result["source"],
            "language": result["language"],
            "available_languages": manual_languages,
            "lyrics": lyrics,
            "lrc": lrc,
        })

    except Exception as e:

        print("ERROR:", repr(e))

        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

def clean_summary(summary):
    # Hapus bold / italic Markdown
    summary = re.sub(r"\*\*(.*?)\*\*", r"\1", summary)
    summary = re.sub(r"__(.*?)__", r"\1", summary)
    summary = re.sub(r"\*(.*?)\*", r"\1", summary)
    summary = re.sub(r"_(.*?)_", r"\1", summary)
    # Hapus heading Markdown
    summary = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        summary,
        flags=re.MULTILINE,
    )

    # Ubah bullet Markdown menjadi bullet biasa
    summary = re.sub(
        r"^\s*[-*+]\s+",
        "• ",
        summary,
        flags=re.MULTILINE,
    )

    # Hapus backtick
    summary = summary.replace("`", "")

    # Ganti semicolon dengan titik
    summary = summary.replace(";", ".")

    # Rapikan spasi di akhir setiap baris
    summary = "\n".join(
        line.rstrip()
        for line in summary.splitlines()
    )

    # Maksimal satu baris kosong antar paragraf
    summary = re.sub(
        r"\n{3,}",
        "\n\n",
        summary,
    )

    return summary.strip()

@csrf_exempt
def summarize_lyrics_api(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "error": "Only POST method is allowed",
                "code": "METHOD_NOT_ALLOWED",
            },
            status=405,
        )

    try:
        data = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "error": "Invalid JSON",
                "code": "INVALID_JSON",
            },
            status=400,
        )

    lyrics = data.get("lyrics")

    if not lyrics:
        return JsonResponse(
            {
                "error": "Lyrics are required",
                "code": "MISSING_LYRICS",
            },
            status=400,
        )

    # Buat hash berdasarkan isi lirik
    lyrics_hash = hashlib.sha256(
        lyrics.strip().encode("utf-8")
    ).hexdigest()

    # Cek cache
    cached = SummaryCache.objects.filter(
        lyrics_hash=lyrics_hash
    ).first()

    if cached:
        print("SUMMARIZE: menggunakan cache")

        return JsonResponse({
            "summary": cached.summary,
            "cached": True,
        })

    print("SUMMARIZE: menerima lirik")
    print("SUMMARIZE: jumlah karakter:", len(lyrics))
    print("SUMMARIZE: cache tidak ditemukan")

    # Retry Gemini jika mengalami 503
    max_retries = 3

    for attempt in range(max_retries):
        try:
            print(
                f"SUMMARIZE: memanggil Gemini "
                f"(percobaan {attempt + 1}/{max_retries})"
            )

            summary = summarize_lyrics(lyrics)
            # bersihkan format markdown dari gemini
            summary = clean_summary(summary)

            print("SUMMARIZE: Gemini berhasil")

            # Simpan hasil ke database
            SummaryCache.objects.create(
                lyrics_hash=lyrics_hash,
                summary=summary,
            )

            print("SUMMARIZE: hasil disimpan ke cache")

            return JsonResponse({
                "summary": summary,
                "cached": False,
            })

        except Exception as e:

            error_text = repr(e)

            print("SUMMARIZE ERROR:", error_text)

            # Cek apakah error berasal dari server Gemini (503)
            if "503" in error_text or "UNAVAILABLE" in error_text:

                if attempt < max_retries - 1:
                    wait_time = 2 ** (attempt + 1)

                    print(
                        f"SUMMARIZE: Gemini sedang sibuk. "
                        f"Retry dalam {wait_time} detik..."
                    )

                    time.sleep(wait_time)
                    continue

                # Semua retry gagal
                return JsonResponse(
                    {
                        "error": (
                            "Layanan AI sedang sibuk. "
                            "Silakan coba lagi beberapa saat."
                        ),
                        "code": "AI_SERVICE_UNAVAILABLE",
                    },
                    status=503,
                )

            # Error selain 503
            return JsonResponse(
                {
                    "error": "Failed to summarize lyrics",
                    "code": "SUMMARIZATION_ERROR",
                },
                status=500,
            )

@csrf_exempt
@api_view(["POST"])
def available_languages(request):

    url = request.data.get("url")

    if not url:
        return Response(
            {
                "error": "YouTube URL is required",
                "code": "MISSING_URL",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        url = clean_youtube_url(url)

    except ValueError as e:
        return Response(
            {
                "error": str(e),
                "code": "INVALID_URL"
            }
            )

    try:
        result = get_manual_subtitles(url)

        return Response({
            "video_id": result["info"].get("id"),
            "title": result["info"].get("title"),
            "languages": result["manual_languages"],
        })

    except Exception:

        return Response(
            {
                "error": "Video tidak dapat diakses. Pastikan video bersifat publik atau unlisted dan caption tersedia.",
                "code": "YOUTUBE_ERROR",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
