import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

# Use Redis as broker
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in each app
app.autodiscover_tasks()
