from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

print 'here 1'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

print 'here 2'

# set up celery app and collect tasks
app = Celery('windfriendly')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

print 'here 3'


# construct crontab
app.conf.CELERYBEAT_SCHEDULE = dict()
app.conf.CELERYBEAT_SCHEDULE.update({
    'update_%s' % ba_name: {
        'task': 'windfriendly.tasks.update',
        'schedule': crontab(minute='*/5'),
        'kwargs': {'ba_name': ba_name},
    } for ba_name in ['bpa', 'miso', 'pjm', 'isone', 'caiso']
})


print 'here 4'


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
    
