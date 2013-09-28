from django.core.management import base
from workers import tasks, utils

class Command(base.BaseCommand):
    def handle(self, *args, **kwargs):
        updated_bas = tasks.update_bas(['BPA', 'ISONE', 'MISO'])
        utils.perform_scheduled_tasks()
        tasks.send_ne_texts_if_necessary()
        print (updated_bas)
