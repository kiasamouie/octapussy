# youtubedl/tasks.py
import random, time
from celery import shared_task
from django.db import transaction
from core.tasks_base import TrackedTask
from core.utils.ytdlp import YoutubeDLHelper
from .serializers import TrackSerializer, PlaylistSerializer

@shared_task(bind=True, base=TrackedTask)
def scrape_artist_task(self, url, **kwargs):
    ydl = YoutubeDLHelper()
    response = {"results": {"success": [], "error": []}}
    urls = ydl.scrape_artist(url)
    for i, u in enumerate(urls):
        try:
            ydl.extract_info(u)

            if ydl.type == "track":
                serializer = TrackSerializer(data=ydl.info[0], ydl=ydl)
            else:
                serializer = PlaylistSerializer(data=ydl.info[0], ydl=ydl)

            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()

                response["results"]["success"].append({
                    "path": ydl.path,
                    "url": ydl.url,
                    "type": ydl.type,
                    "platform": ydl.platform,
                    "id": getattr(instance, "id", None),
                    "upload_id": getattr(instance, "upload_id", None),
                })
            else:
                response["results"]["error"].append({
                    "path": ydl.path,
                    "url": ydl.url,
                    "type": ydl.type,
                    "platform": ydl.platform,
                    "errors": serializer.errors,
                })

        except Exception as e:
            response["results"]["error"].append({
                "path": getattr(ydl, "path", None),
                "url": u,
                "type": getattr(ydl, "type", None),
                "platform": getattr(ydl, "platform", None),
                "errors": str(e),
            })

        if 0 < i < len(urls) - 1:
            time.sleep(random.uniform(5, 10))

    
    return response

