#!/bin/bash

sudo pip install south
python manage.py syncdb
python manage.py migrate windfriendly 0001 --fake
python manage.py migrate workers 0001 --fake
python manage.py migrate allauth.socialaccount 0012 --fake
python manage.py migrate accounts 0001 --fake
python manage.py migrate allauth.socialaccount.providers.facebook 0004 --fake
