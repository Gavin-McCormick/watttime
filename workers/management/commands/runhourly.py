from django.core.management import base
from workers import tasks

class Command(base.BaseCommand):
    def handle(self, *args, **kwargs):
        updated_bas = tasks.update_bas(['CAISO'])
        print (updated_bas)
