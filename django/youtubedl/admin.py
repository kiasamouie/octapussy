from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import admin, messages
from .models import Track, Playlist, Thumbnail
from mix.models import Mix  # assuming Mix is in another app


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "uploader",
        "genre",
        "webpage_url", 
        "timestamp",
        "duration",
        "view_count",
        "like_count",
        "comment_count",
        "repost_count", 
    )
    search_fields = ("title", "uploader", "upload_id", "genre", "webpage_url")
    list_filter = ("extractor", "genre", "timestamp")
    date_hierarchy = "timestamp"
    ordering = ("-id",)

    actions = ["create_mix_from_tracks"]
    
    change_list_template = "admin/playlist_changelist.html"

    def create_mix_from_tracks(self, request, queryset):
        if not queryset.exists():
            self.message_user(request, "No tracks selected.", level=messages.WARNING)
            return

        # Build a querystring with selected IDs
        ids = ",".join(str(t.id) for t in queryset)
        return redirect(f"/admin/mix/mix/add/?tracks={ids}")

    create_mix_from_tracks.short_description = "Create Mix from selected tracks"


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "upload_id", "webpage_url", "create_mix_button")
    search_fields = ("title", "upload_id", "webpage_url", "extractor", "extractor_key")
    list_filter = ("extractor",)
    autocomplete_fields = ("tracks",)
    ordering = ("-id",)
    
    change_list_template = "admin/playlist_changelist.html" 
   
    def create_mix_button(self, obj):
        if not obj.tracks.exists():
            return "-"
        track_ids = ",".join(str(t.id) for t in obj.tracks.all())
        url = reverse("admin:mix_mix_add") + f"?tracks={track_ids}&title={obj.title}"
        return format_html(
            '<a class="button" style="padding:2px 6px; white-space:nowrap;" href="{}">Create Mix</a>',
            url,
        )

    create_mix_button.short_description = "Mix"
    create_mix_button.allow_tags = True
    
    actions = ["create_mix_from_playlist"]
    
    def create_mix_from_playlist(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one playlist.", level=messages.WARNING)
            return

        playlist = queryset.first()
        tracks = playlist.tracks.all()

        if not tracks.exists():
            self.message_user(request, f"No tracks found in playlist '{playlist.title}'.", level=messages.WARNING)
            return

        ids = ",".join(str(t.id) for t in tracks)
        return redirect(f"/admin/mix/mix/add/?tracks={ids}&title={playlist.title}")

    create_mix_from_playlist.short_description = "Create mix from selected playlist"


@admin.register(Thumbnail)
class ThumbnailAdmin(admin.ModelAdmin):
    list_display = ("id", "track", "url", "width", "height")
    search_fields = ("track__title", "url")
    list_filter = ("width", "height")
    autocomplete_fields = ("track",)
    ordering = ("-id",)
