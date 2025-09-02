from django.db import models

class Playlist(models.Model):
    title = models.CharField(max_length=255)
    user = models.CharField(max_length=1024,blank=True,null=True)

    def __str__(self):
        return self.title
