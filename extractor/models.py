from django.db import models

# Create your models here.

class SummaryCache(models.Model):
    lyrics_hash = models.CharField(max_length=64, unique=True)
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.lyrics_hash