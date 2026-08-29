"""
Celery configuration for BramTech VTU.
Handles async task queue for VTU delivery, reconciliation, and refunds.
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("bramtech_vtu")

# Load config from Django settings, using CELERY_ namespace
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Test task for verifying Celery works."""
    print(f"Request: {self.request!r}")