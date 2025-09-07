from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta, datetime
import pytz
import uuid

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Profile for {self.user.username}'

class LogEntry(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return f'LogEntry(id={self.id}) at {self.created_at} with message "{self.message}"'

class TaskJob(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        STARTED = "STARTED"
        SUCCESS = "SUCCESS"
        FAILURE = "FAILURE"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, db_index=True)
    task_id = models.CharField(max_length=100, db_index=True, null=True, blank=True)  # Celery task id
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    params = models.JSONField(null=True, blank=True)
    result = models.JSONField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)

    scheduled_for = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} [{self.status}] {self.id}"
