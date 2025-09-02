from rest_framework import serializers
from .models import Playlist

class PlaylistSerializer(serializers.ModelSerializer):
    # tracks = TrackSerializer(many=True)
    class Meta:
        model = Playlist
        fields = "__all__"