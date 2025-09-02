from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta, datetime
import pytz

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