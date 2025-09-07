from django.contrib import admin
from .models import Mix

@admin.register(Mix)
class MixAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "created_at", "uploaded_at")
    search_fields = ("name", "description", "tracks__title")
    list_filter = ("status", "created_at", "uploaded_at")
    autocomplete_fields = ("tracks",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        tracks_param = request.GET.get("tracks")
        if tracks_param:
            track_ids = [int(pk) for pk in tracks_param.split(",") if pk.isdigit()]
            initial["tracks"] = track_ids
        return initial

    actions = ["mark_as_uploaded"]

    def mark_as_uploaded(self, request, queryset):
        updated = queryset.update(status=Mix.Status.UPLOADED)
        self.message_user(request, f"{updated} mixes marked as uploaded.")