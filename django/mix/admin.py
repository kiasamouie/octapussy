from django.contrib import admin
from .models import Mix

@admin.register(Mix)
class MixAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_at", "uploaded_at")
    search_fields = ("title", "description", "tracks__title")
    list_filter = ("status", "created_at", "uploaded_at")
    autocomplete_fields = ("tracks",)
    date_hierarchy = "created_at"
    ordering = ("-id",)
    
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        title = request.GET.get("title")
        if title:
            initial["title"] = title
        tracks = request.GET.get("tracks")
        if tracks:
            initial["tracks"] = [int(pk) for pk in tracks.split(",") if pk]
        return initial

    actions = ["mark_as_uploaded"]

    def mark_as_uploaded(self, request, queryset):
        updated = queryset.update(status=Mix.Status.UPLOADED)
        self.message_user(request, f"{updated} mixes marked as uploaded.")