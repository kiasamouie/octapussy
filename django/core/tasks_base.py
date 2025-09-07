# django/core/tasks_base.py
from celery import Task
from django.utils import timezone
from core.models import TaskJob

class TrackedTask(Task):
    """Base Celery task that automatically syncs TaskJob by job_id in kwargs."""
    abstract = True
    job_lookup_kwarg = "job_id"

    def _get_job(self, kwargs):
        job_id = kwargs.get(self.job_lookup_kwarg)
        if not job_id:
            return None
        return TaskJob.objects.filter(id=job_id).first()

    def before_start(self, task_id, args, kwargs):
        job = self._get_job(kwargs)
        if job:
            job.task_id = task_id
            job.status = TaskJob.Status.STARTED
            job.started_at = timezone.now()
            job.save(update_fields=["task_id", "status", "started_at", "updated_at"])

    def on_success(self, retval, task_id, args, kwargs):
        job = self._get_job(kwargs)
        if job:
            job.status = TaskJob.Status.SUCCESS
            job.result = retval if isinstance(retval, (dict, list)) else {"result": str(retval)}
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "result", "finished_at", "updated_at"])

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        job = self._get_job(kwargs)
        if job:
            job.status = TaskJob.Status.FAILURE
            job.error = str(exc)
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "error", "finished_at", "updated_at"])