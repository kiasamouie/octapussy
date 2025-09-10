from django.db import models
from django.utils import timezone


class Mix(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"
        UPLOADED = "uploaded", "Uploaded"

    title = models.CharField(max_length=255, help_text="Friendly name for this mix")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    audio_file = models.FileField(upload_to="mixes/audio/", blank=True, null=True)
    video_file = models.FileField(upload_to="mixes/video/", blank=True, null=True)
    info_file = models.FileField(upload_to="mixes/info/", blank=True, null=True)

    tracks = models.ManyToManyField("youtubedl.Track", related_name="mixes")

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    error_message = models.TextField(blank=True, null=True)

    upload_url = models.URLField(blank=True, null=True, help_text="Link to YouTube or other platform")
    uploaded_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Mix {self.id} - {self.title or 'Untitled'} [{self.status}]"
