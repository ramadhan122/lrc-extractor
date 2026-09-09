from django.urls import path
from .views import (
    extract_lyrics,
    available_languages,
    )

from .views import (
    extract_lyrics,
    available_languages,
)

urlpatterns = [
    path(
        "extract/",
        extract_lyrics
        ),

        path(
            "languages/",
            available_languages
        ),
]
