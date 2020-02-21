from django.db import models

# Create your models here.
class ProcessedSong(models.Model):
    hash_code = models.CharField(max_length=32, primary_key=True)
    procesed_song_url = models.URLField(max_length=200)

    def __str__(self):
        return self.hash_code