watttime
========

How clean is your energy, right now?


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

* Set up environment variables in your environment (for example in your .bashrc file). The list of environmental variables that need to be externally set can be found at the top of the settings.py file. Create a file called .bashrc in your root directory. You can do this by opening your shell and tying ````touch .bashrc````. Edit this file by typing ````vi .bashrc````. You can then paste the environmental variables. Hit ````esc```` and ````:x```` to exit. In MacOS you may need to add the line ````source ~/.bashrc```` to .bash_profile file in your home directory. This directs it to look at .bashrc for the list of environment variables.

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


Edit
-----------
We're using a variant of the branching model in [git flow](http://nvie.com/posts/a-successful-git-branching-model/).
The main points of the added complexity are to keep the <code>master</code> branch deployable,
to share in-progress feature branches early and often,
and to have the <code>develop</code> branch be a staging ground for merging finished features.

* If you're in <code>master</code> and don't have <code>develop</code> yet:
    ````
    git checkout -b develop
    git pull origin develop
    ````

* To start a new feature (change <code>myfeature</code> to something appropriate):
    ````
    git checkout develop
    git pull origin develop
    git checkout -b myfeature develop
    # edit some things
    # commit the edits
    git push origin myfeature
    ````

* To merge a feature branch into the main development/staging branch:
    ````
    git checkout develop
    git pull origin develop
    git merge --no-ff myfeature
    git push origin develop
    ````
