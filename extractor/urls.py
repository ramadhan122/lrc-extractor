from django.urls import path
from .views import (
    home,
    extract_lyrics,
    available_languages,
    summarize_lyrics_api,
)

urlpatterns = [
    path("", home),
    path("api/extract/", extract_lyrics),
    path("api/languages/", available_languages),
    path("api/summarize/", summarize_lyrics_api),
]