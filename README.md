watttime
========

How green is your energy, right now?


Install
-------
* Clone this repo.
* Install the [Heroku toolbelt](https://toolbelt.heroku.com/), then:
    ````
    cd watttime
    heroku login
    heroku git:remote -a watttime
    ````

* Install dependencies: Install pip from http://www.pip-installer.org/en/latest/installing.html (bottom of page under "Installing from source"), then
    ````
    sudo pip install -r requirements.txt
    ````    

* Set up models (follow instructions for syncdb):
    ````
    python manage.py syncdb
    ./south_startup.sh
    python manage.py migrate
    # if migrate asks you to delete anything, say no then rerun the command
    ````

Upgrade
---------
````
sudo pip install -r requirements.txt
python manage.py syncdb
python manage.py migrate
````
If migrate asks you to delete anything, say 'no' then rerun the command.

Usage
-------
* ````python manage.py runserver 8000````
* Open http://localhost:8000 in a browser
