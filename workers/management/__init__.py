# This file is required for manage.py to recognize the custom commands
# defined in commands/

# To create a custom command for an app:
# Create a subfolder app/management/commands
# Create empty files
#   app/__init__.py (don't know if this one is necessary)
#   app/management/__init__.py
#   app/management/commands/__init__.py
# Create a file called
#   app/management/commands/<commandname>.py,
# which should contain a class called 'Command' extending
#   django.core.management.base.BaseCommand
# and defining a method 'handle(*args, **kwargs)'.
