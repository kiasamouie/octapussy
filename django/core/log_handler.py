# log_handler.py
import logging
from django.db import models

class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        try:
            from core.models import LogEntry
            message = self.format(record)
            LogEntry.objects.create(message=message)
        except Exception:
            pass  # You might want to handle exceptions or at least pass them silently.
