from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .services.parser import parse_vtt
from .services.normalizer import normalize_lyrics
from .services.lrc import generate_lrc
from .services.url import clean_youtube_url
from .services.youtube import(
    extract_subtitle,
    get_manual_subtitles,
)


@api_view(["POST"])
def extract_lyrics(request):

    url = request.data.get("url")

    if not url:
        return Response(
            {"error": "YouTube URL is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    url = clean_youtube_url(url)
    print("CLEAN_URL:", url)

    language = request.data.get("language", "en")

    try:

        print("STEP 1 - extracting subtitle")
        
        result = extract_subtitle(
            url,
            language
        )

        print("STEP 2 - subtitle extracted")

        if not result["content"]:
            return Response({
                "error": "English subtitle not found"
            })

        print("STEP 3 - parsing VTT")

        lyrics = parse_vtt(
            result["content"]
        )

        lyrics = normalize_lyrics(
            lyrics
        )

        lrc = generate_lrc(
            lyrics
        )

        print("STEP 4 - parser success")

        return Response({
            "video_id": result["info"].get("id"),
            "title": result["info"].get("title"),
            "source": result["source"],
            "language": language,
            "lyrics": lyrics,
            "lrc": lrc,
        })
    
    except Exception as e:
    
            print("ERROR:", repr(e))
    
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

def available_languages(request):

    url = request.data.get("url")
    if not url:
        return Response(
            {"error": "youtube URL is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        result = get_manual_subtitles(url)

        return Response({
            "videdo_id": result["info"].get("id"),
            "title": result["info"].get("title"),
            "languages": result["languages"],
        })

    except Exception as e:

        print("ERROR:", repr(e))

        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )