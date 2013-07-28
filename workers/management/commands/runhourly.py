from django.core.management import base
from workers import tasks

class Command(base.BaseCommand):
    def handle(self):
        updated_bas = tasks.update_bas(['CAISO'])
        print (updated_bas)
