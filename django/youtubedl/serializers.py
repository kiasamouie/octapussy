from rest_framework import serializers
from .models import Track, Playlist, Thumbnail
from datetime import datetime, timezone
import json

class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ['url', 'width', 'height']

class TrackSerializer(serializers.ModelSerializer):
    thumbnails = ThumbnailSerializer(many=True, write_only=True)

    class Meta:
        model = Track
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        ydl = kwargs.pop('ydl', None)
        data = kwargs.get('data', None)
        if ydl:
            data = ydl.info[0]
        if data:
            data['upload_id'] = data['id']
            
            if 'timestamp' in data:
                data['timestamp'] = datetime.fromtimestamp(data['timestamp'], tz=timezone.utc)
            elif 'upload_date' in data:
                data['timestamp'] = datetime.strptime(data['upload_date'], "%Y%m%d")

            for thumbnail in data['thumbnails']:
                for k in ['id', 'preference', 'resolution']:
                    if k in thumbnail:
                        del thumbnail[k]
            default_fields = {
                'view_count': 0,
                'like_count': 0,
                'comment_count': 0,
                'genre': '',
                'vcodec': 0,
                'video_ext': 0
            }
            for k, default in default_fields.items():
                if data.get(k) is None or data[k] == "none":
                    data[k] = default
            
            remove_keys = [
                'id', '__last_playlist_index', '_filename', '_has_drm', '_type', '_version',
                'aspect_ratio', 'audio_ext', 'description', 'display_id', 'duration_string',
                'epoch', 'filename','filesize_approx','format_id', 'format', 'formats', 'fulltitle','genres', 
                'http_headers','license', 'n_entries', 'original_url', 'playlist_autonumber', 
                'playlist_count','playlist_id', 'playlist_index', 'playlist_title', 
                'playlist_uploader_id','playlist_uploader', 'playlist', 'preference', 'protocol', 
                'release_year','requested_subtitles', 'resolution', 'thumbnail', 'upload_date','url', 'vbr', 
                'video_ext'
            ]
            for k in remove_keys:
                if k in data:
                    del data[k]
            
            kwargs['data'] = data
        super().__init__(*args, **kwargs)
    
    def to_representation(self, instance):
        """
        Remove the 'thumbnails' field from the serialized output.
        """
        representation = super().to_representation(instance)
        representation.pop('thumbnails', None)  # Remove 'thumbnails' from the output
        return representation

    def create(self, validated_data):
        thumbnails = validated_data.pop('thumbnails', [])
        track = Track.objects.create(**validated_data)
        for thumbnail in thumbnails:
            Thumbnail.objects.create(track=track, **thumbnail)
        return track

    def update(self, instance, validated_data):
        thumbnails = validated_data.pop('thumbnails', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update thumbnails
        instance.thumbnails.all().delete()
        for thumbnail in thumbnails:
            Thumbnail.objects.create(track=instance, **thumbnail)
        
        return instance

class PlaylistSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True)
    class Meta:
        model = Playlist
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        ydl = kwargs.pop('ydl', None)
        if ydl:
            data = ydl.info[0]
            kwargs['data'] = {
                'title': data['playlist_title'],
                'upload_id': data['playlist_id'],
                'extractor': data['extractor'],
                'extractor_key': data['extractor_key'],
                'webpage_url': ydl.url,
                'tracks': []
            }
            for track in ydl.info:
                track_serializer = TrackSerializer(data=track)
                if track_serializer.is_valid():
                    kwargs['data']['tracks'].append(track_serializer.validated_data)
                else:
                    print(track_serializer.errors)
                    exit(track_serializer.errors)
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        tracks = validated_data.pop('tracks', [])
        playlist = Playlist.objects.create(**validated_data)
        for track in tracks:
            thumbnails = track.pop('thumbnails', [])
            track = Track.objects.create(**track)
            for thumbnail in thumbnails:
                Thumbnail.objects.create(**thumbnail, track=track)
            playlist.tracks.add(track)
        return playlist
    
    def update(self, instance, validated_data):
        tracks = validated_data.pop('tracks', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update tracks and their thumbnails
        instance.tracks.all().delete()
        for track in tracks:
            thumbnails = track.pop('thumbnails', [])
            track = Track.objects.create(**track)
            for thumbnail in thumbnails:
                Thumbnail.objects.create(**thumbnail, track=track)
            instance.tracks.add(track)
        
        return instance