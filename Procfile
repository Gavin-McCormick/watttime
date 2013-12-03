web: python manage.py collectstatic --noinput; gunicorn wsgi -w 1
worker: celery -A windfriendly worker -l info -B -c 1