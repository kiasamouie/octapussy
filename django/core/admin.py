from django.contrib import admin
from .models import LogEntry, Profile, TaskJob
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import admin
from .models import TaskJob
from django_celery_results.models import TaskResult

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "message")
    ordering = ("-id",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone_number", "address")
    ordering = ("-id",)


@admin.register(TaskJob)
class TaskJobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "task_link",
        "status",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)

    def task_link(self, obj):
        if not obj.task_id:
            return "-"
        try:
            task = TaskResult.objects.get(task_id=obj.task_id)
            url = reverse("admin:django_celery_results_taskresult_change", args=[task.id])
            return format_html('<a href="{}">{}</a>', url, obj.task_id)
        except TaskResult.DoesNotExist:
            return obj.task_id

    task_link.short_description = "Task ID"
