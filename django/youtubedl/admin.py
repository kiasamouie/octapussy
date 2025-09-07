from django.urls import path
from django.shortcuts import redirect
from django.contrib import admin, messages
from .models import Track, Playlist, Thumbnail
from mix.models import Mix  # assuming Mix is in another app


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "uploader",
        "upload_id",
        "duration",
        "view_count",
        "timestamp",
    )
    search_fields = ("title", "uploader", "upload_id", "genre", "webpage_url")
    list_filter = ("extractor", "genre", "timestamp")
    date_hierarchy = "timestamp"
    ordering = ("-timestamp",)

    actions = ["create_mix_from_tracks"]

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
    list_display = ("id", "title", "upload_id", "extractor", "extractor_key")
    search_fields = ("title", "upload_id", "extractor", "extractor_key")
    list_filter = ("extractor",)
    autocomplete_fields = ("tracks",)
    ordering = ("title",)


@admin.register(Thumbnail)
class ThumbnailAdmin(admin.ModelAdmin):
    list_display = ("id", "track", "url", "width", "height")
    search_fields = ("track__title", "url")
    list_filter = ("width", "height")
    autocomplete_fields = ("track",)
