watttime
========

How green is your energy, right now?


Install
-------
* Get code:
    ````
    mkdir watttime
    cd watttime
    git init
    heroku login
    heroku git:remote -a watttime
    git pull heroku master
    ````

* Install dependencies: Install pip from http://www.pip-installer.org/en/latest/installing.html (bottom of page under "Installing from source"), then
    ````
    cd watttime
    sudo pip install -r requirements.txt
    ````    

* Set up models (follow instructions for syncdb):
    ````
    python manage.py syncdb
    ./south_startup.sh
    python manage.py migrate
    # say 'no' if migrate asks you to delete anything, then rerun the command
    ````

Upgrade
---------
````
sudo pip install -r requirements.txt
python manage.py syncdb
python manage.py migrate
````
Say 'no' if migrate asks you to delete anything, then rerun the command.

Usage
-------
* ````python manage.py runserver 8000````
* Open http://localhost:8000 in a browser
