from django.db import models

class Track(models.Model):
    title = models.CharField(max_length=255)
    s3_file_url = models.URLField(max_length=1024,blank=True,null=True)
    s3_file_key = models.CharField(max_length=1024,blank=True,null=True)
    upload_id = models.CharField(max_length=255)
    uploader = models.CharField(max_length=255)
    uploader_id = models.CharField(max_length=255)
    uploader_url = models.URLField(max_length=1024)
    timestamp = models.DateTimeField()
    duration = models.FloatField()
    webpage_url = models.URLField(max_length=1024)
    view_count = models.BigIntegerField()
    like_count = models.BigIntegerField()
    comment_count = models.BigIntegerField()
    repost_count = models.BigIntegerField(blank=True,null=True)
    genre = models.CharField(max_length=50, blank=True)
    webpage_url_basename = models.CharField(max_length=255)
    webpage_url_domain = models.CharField(max_length=255)
    extractor = models.CharField(max_length=50)
    extractor_key = models.CharField(max_length=50)
    tbr = models.FloatField(null=True)
    ext = models.CharField(max_length=10)

    def __str__(self):
        return self.title

class Playlist(models.Model):
    title = models.CharField(max_length=255)
    upload_id = models.CharField(max_length=255)
    extractor = models.CharField(max_length=50)
    extractor_key = models.CharField(max_length=50)
    webpage_url = models.URLField(max_length=1024)
    tracks = models.ManyToManyField(Track, related_name='playlists')

    def __str__(self):
        return self.title

class Thumbnail(models.Model):
    track = models.ForeignKey(Track, related_name='thumbnails', on_delete=models.CASCADE)
    url = models.URLField()
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)

    def __str__(self):
        display_text = f"{self.width}x{self.height}" if self.width and self.height else "original"
        return f'{self.track.title} - {display_text}'
