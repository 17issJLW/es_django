from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, platforms
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'es_django.settings')

app = Celery('es_django')
app.config_from_object('django.conf:settings', namespace='CELERY')
platforms.C_FORCE_ROOT = True
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))