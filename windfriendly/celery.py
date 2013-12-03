from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# set up celery app and collect tasl
app = Celery('workers')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# construct crontab
app.conf.CELERYBEAT_SCHEDULE = dict()
app.conf.CELERYBEAT_SCHEDULE.update({
    'update_%s' % ba_name: {
        'task': 'windfriendly.tasks.update',
        'schedule': crontab(minute='*/5'),
        'kwargs': {'ba_name': ba_name},
    } for ba_name in ['bpa', 'miso', 'pjm', 'isone', 'caiso']
})


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
    
