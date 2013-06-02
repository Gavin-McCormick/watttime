watttime
========

How green is your energy, right now?


Install
-------
* Get code:

    mkdir watttime
    cd watttime
    git init
    heroku login
    heroku git:remote -a watttime
    git pull heroku master

* Install pip from http://www.pip-installer.org/en/latest/installing.html (bottom of page under "Installing from source")

* Set up and run django server (follow instructions for syncdb):

    cd watttime
    sudo pip install -r requirements.txt
    python manage.py syncdb
    python manage.py runserver 8000

* Open http://localhost:8000 in a browser
