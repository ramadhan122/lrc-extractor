from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import render
from .services.parser import parse_vtt
from .services.normalizer import normalize_lyrics
from .services.lrc import generate_lrc
from .services.url import clean_youtube_url
from .services.youtube import(
    extract_subtitle_data,
    get_manual_subtitles,
)

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
            "error": "Gagal mendapatkan informasi video",
            "error": "YOUTUBE_ERROR",
            },
            status=status.HTTP_400_BAD_REQUEST,
        ),
