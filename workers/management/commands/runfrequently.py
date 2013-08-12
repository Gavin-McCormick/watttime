from django.core.management import base
from workers import tasks, utils

class Command(base.BaseCommand):
    def handle(self, **kwargs):
        updated_bas = tasks.update_bas(['BPA', 'ISONE'])
        utils.perform_scheduled_tasks()
        tasks.send_ne_texts_if_necessary()
        pushes = [tasks.push_ba_updates(ba) for ba in ['BPA', 'ISONE']]
        print (updated_bas)
