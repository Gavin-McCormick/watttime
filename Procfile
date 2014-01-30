web: python manage.py collectstatic --noinput; gunicorn wsgi -w 1
worker: python manage.py celery -A windfriendly worker -l info -c 1
cscheduler: python manage.py celery worker -A windfriendly -B -E --maxtasksperchild=1000

