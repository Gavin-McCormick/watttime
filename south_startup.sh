#!/bin/bash

python manage.py syncdb
python manage.py migrate accounts 0001
python manage.py migrate windfriendly 0001
python manage.py migrate workers 0001
python manage.py migrate allauth.socialaccount 0001
python manage.py migrate allauth.socialaccount.providers.facebook 0001
python manage.py migrate sms_tools 0001
python manage.py migrate
