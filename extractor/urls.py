from django.urls import path
from .views import extract_lyrics

urlpatterns = [
    path("extract/", extract_lyrics),
]
