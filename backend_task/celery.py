from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_task.settings')

app = Celery('backend_task')

app.config_from_object('django.conf:settings', namespace='CELERY')

# task modules loading
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'send-birthday-wishes': {
        'task': 'orbit.tasks.send_birthday_wishes',
        'schedule': 86400.0,  
        'options': {'expires': 3600 * 23}  # after 23 hours, it expires
    },
}
app.conf.timezone = 'UTC'