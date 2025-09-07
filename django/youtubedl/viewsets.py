import os
import re
import random
import time
from urllib.parse import quote

from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Track, Playlist, Thumbnail
from .serializers import TrackSerializer, PlaylistSerializer
from django.db import transaction

from core.utils.ytdlp import YoutubeDLHelper
from core.utils.socials.youtube import YouTubeAPI
from core.models import TaskJob
from .tasks import scrape_artist_task

class YoutubeDLViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def list(self, request):
        try:
            if request.query_params.get('type') is None:
                return Response(data={'msg': 'Type missing'}, status=status.HTTP_400_BAD_REQUEST)

            if request.query_params.get('type') == 'tracks':
                queryset = Track.objects.all()
                serializer = TrackSerializer(queryset, many=True)
            else:
                queryset = Playlist.objects.all()
                serializer = PlaylistSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=["post"], detail=False)
    def scrape(self, request):
        try:
            urls = request.data.get("urls") or request.data.get("url")
            if not urls:
                return Response(
                    {"detail": "url or urls is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not isinstance(urls, list):
                urls = [urls]

            jobs = []
            for url in urls:
                job = TaskJob.objects.create(
                    name="scrape_artist_task",
                    params={"url": url},
                    status=TaskJob.Status.PENDING,
                )
                async_res = scrape_artist_task.delay(url=url, job_id=str(job.id))
                job.task_id = async_res.id
                job.save(update_fields=["task_id", "updated_at"])

                jobs.append(
                    {
                        "job_id": str(job.id),
                        "task_id": async_res.id,
                        "status": job.status,
                        "url": url,
                    }
                )

            return Response(jobs, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
    @action(methods=['post'], detail=False)
    def download(self, request):
        try:
            # init test
            youtube_api = YouTubeAPI(email=request.data["email"])
            # return Response(data=request.data, status=status.HTTP_200_OK)

            # upload video
            video_file = os.path.join("django", "BACKGROUND.mp4")
            title = "Test Video Upload"
            description = request.data["description"]
            category_id = "22"
            tags = ["test", "video", "upload"]
            video_id = youtube_api.upload_video(video_file, title, description, category_id, tags)
            return Response(data={"video_id":f"https://www.youtube.com/watch?v={video_id}"}, status=status.HTTP_200_OK)

            # get comments by video id
            # comments = youtube_api.get_video_comments(request.data["video_id"], max_results=50)
            # return Response({"comments": comments}, status=status.HTTP_200_OK)

            # reply to comment by parentId
            # new_comment = youtube_api.reply_to_comment(request.data["parentId"], request.data["reply_text"])
            # return Response({"comment": new_comment}, status=status.HTTP_200_OK)

            # download
            ydl = YoutubeDLHelper(request.data["url"])
            response = {
                'success': True,
                'info': ydl.info,
                'path': ydl.path,
                'url': ydl.url,
                'type': ydl.type,
                'platform': ydl.platform,
                'download': ydl.download(),
            }

            if ydl.type == 'track':
                serializer = TrackSerializer(data=ydl.info[0], ydl=ydl)
            else:
                serializer = PlaylistSerializer(data=ydl.info[0], ydl=ydl)

            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()
                response.update({
                    'id': getattr(instance, 'id', None),
                    'upload_id': getattr(instance, 'upload_id', None),
                })

            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=False)
    def save_track(self, request):
        try:
            file_path = request.data.get("dir")
            escaped_path = re.sub(r'(:)', r'\\:', re.sub(r'(\s)', r'\\ ', file_path))

            if os.path.isfile(file_path):
                file_handle = open(file_path, 'rb')
                response = FileResponse(file_handle, as_attachment=True, filename=os.path.basename(file_path))
                response['Content-Disposition'] = f'attachment; filename=\"{os.path.basename(file_path)}\"'
                return response

            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['get'], detail=False)
    def stats(self, request):
        try:
            return Response([
                {
                    'title': 'Tracks',
                    'total': Track.objects.count(),
                    'rate': '0.43%',
                    'levelUp': True,
                    'levelDown': False,
                    'icon': 'faMusic'
                },
                {
                    'title': 'Playlists',
                    'total': Playlist.objects.count(),
                    'rate': '0.43%',
                    'levelUp': True,
                    'levelDown': False,
                    'icon': 'faClipboardList'
                },
                {
                    'title': 'Thumbnails',
                    'total': Thumbnail.objects.count(),
                    'rate': '0.43%',
                    'levelUp': True,
                    'levelDown': False,
                    'icon': 'faImage'
                }
            ], status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)