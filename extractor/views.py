from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .services.parser import parse_vtt
from .services.youtube import extract_subtitle


@api_view(["POST"])
def extract_lyrics(request):

    url = request.data.get("url")

    if not url:
        return Response(
            {"error": "YouTube URL is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:

        print("STEP 1 - extracting subtitle")

        result = extract_subtitle(
            url,
            "en"
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

        print("STEP 4 - parser success")

        return Response({
            "video_id": result["info"].get("id"),
            "title": result["info"].get("title"),
            "source": result["source"],
            "language": "en",
            "lyrics": lyrics,
        })

    except Exception as e:

        print("ERROR:", repr(e))

        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )