from django.db import models


class ProcessedSong(models.Model):
    hash_code = models.CharField(max_length=32, primary_key=True)
    pub_date = models.DateTimeField('date loaded')
    input_url = models.URLField()
    vocal_url = models.URLField()
    accompaniment_url = models.URLField()

    def __str__(self):
        return self.hash_code
