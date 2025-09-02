from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Playlist
from .serializers import PlaylistSerializer

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

# from lofiwifi.source import Source
# from lofiwifi.mix import Mix

class PlaylistViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def list(self, request):
        # if request.query_params.get('type') is None:
        #     return Response(data={'msg': 'Type missing'},status=status.HTTP_400_BAD_REQUEST)

        queryset = Playlist.objects.all()
        serializer = PlaylistSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def create_mix(self, request):
        try:
            source = Source(request.data["url"],save_directory='/media')
            source.Download()
            lofiwifi = Mix(
                source.track_list_data,
                source.tracks_directory,
                # loop=loop,
                # captions=True,
                audio_only=True,
                # audio_type='wav',
                # n_times=6,
                # extra_seconds=2,
                # keep_tracks=True,
                fade_in=2,
                fade_out=2,
            )
            lofiwifi.Create_Mix()
            response = {
                'success': True,
            }
            # return Response(data=response,status=status.HTTP_200_OK)


            return Response(data=response,status=status.HTTP_200_OK)
        except (ObjectDoesNotExist, TokenError):
            return Response(status=status.HTTP_400_BAD_REQUEST)