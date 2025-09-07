from django.contrib import admin
from .models import LogEntry, Profile, TaskJob

# Register your models here.
admin.site.register(LogEntry)
admin.site.register(Profile)
admin.site.register(TaskJob)