from .celery import app as celery_app

default_app_config = "core.apps.CoreConfig"

__all__ = ("celery_app",)