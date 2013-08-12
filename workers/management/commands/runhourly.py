from django.core.management import base
from workers import tasks

class Command(base.BaseCommand):
    def handle(self, **kwargs):
        updated_bas = tasks.update_bas(['CAISO'])
        pushes = tasks.push_ba_updates('CAISO')
        print (updated_bas)
