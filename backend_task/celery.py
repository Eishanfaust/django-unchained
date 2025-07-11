from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from datetime import timedelta


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_task.settings')

app = Celery('backend_task')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for birthday wishes

app.conf.beat_schedule = {
    'send-birthday-wishes': {
        'task': 'orbit.tasks.send_birthday_wishes',
        'schedule': 86400.0,  # 24 hours in seconds (or use `timedelta(days=1)`)
        'options': {'expires': 3600 * 23}  # Expires after 23 hours
    },
}
app.conf.timezone = 'UTC'