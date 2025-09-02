import os
import re
from urllib.parse import quote
from django.http import FileResponse
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Track, Playlist, Thumbnail
from .serializers import TrackSerializer, PlaylistSerializer
from django.core.exceptions import ObjectDoesNotExist
from core.utils.ytdlp import YoutubeDLHelper
from core.utils.socials.youtube import YouTubeAPI

class YoutubeDLViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def list(self, request):
        if request.query_params.get('type') is None:
            return Response(data={'msg': 'Type missing'},status=status.HTTP_400_BAD_REQUEST)
        
        if request.query_params.get('type') == 'tracks':
            queryset = Track.objects.all()
            serializer = TrackSerializer(queryset, many=True)
        else:
            queryset = Playlist.objects.all()
            serializer = PlaylistSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    @action(methods=['post'], detail=False)
    def download(self, request):
        try:
            youtube_api = YouTubeAPI(email=request.data["email"])
            return Response(data=request.data, status=status.HTTP_200_OK)
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
        
            ydl = YoutubeDLHelper(request.data["url"])
            response = {
                'success': False,
                'info': ydl.info,
                'path': ydl.path,
                'url': ydl.url,
                'type': ydl.type,
                'platform': ydl.platform,
                'download': ydl.download(timestamps=request.data["timestamps"]),
            }

            # return Response(data=response, status=status.HTTP_200_OK)

            if ydl.type == 'track':
                result = self.handle_download(ydl, TrackSerializer, Track, ydl.info[0]['id'])
            else:
                result = self.handle_download(ydl, PlaylistSerializer, Playlist, ydl.info[0]['playlist_id'])

            response['is_valid'] = result['is_valid']
            response['errors'] = result['errors']
            response['success'] = result['is_valid']

            return Response(data=response, status=status.HTTP_200_OK)
        except (ObjectDoesNotExist, TokenError) as e:
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def handle_download(self, ydl, serializer_class, model_class, upload_id):
        try:
            instance = model_class.objects.get(upload_id=upload_id)
            serializer = serializer_class(instance, ydl=ydl)
        except model_class.DoesNotExist:
            serializer = serializer_class(ydl=ydl)
        
        if serializer.is_valid():
            instance = serializer.save()
            return {'instance': instance, 'created': instance._state.adding, 'is_valid': True, 'errors': None}
        return {'instance': None, 'created': False, 'is_valid': False, 'errors': serializer.errors}
    
    @action(methods=['post'], detail=False)
    def save_track(self, request):
        try:
            file_path = request.data.get("dir")
            escaped_path = re.sub(r'(:)', r'\\:', re.sub(r'(\s)', r'\\ ', file_path))
            response = {
                'success': False,
                'message': 'File not found',
                'file_path' : file_path,
                'escaped_path' : escaped_path,
            }

            if os.path.isfile(file_path):
                file_handle = open(file_path, 'rb')
                response = FileResponse(file_handle, as_attachment=True, filename=os.path.basename(file_path))
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
            else:
                return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        except (TokenError, KeyError) as e:
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def stats(self, request):
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
