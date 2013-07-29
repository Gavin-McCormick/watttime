from django.core.management import base
from workers import tasks, utils

class Command(base.BaseCommand):
    def handle(self, **kwargs):
        tasks.send_ca_forecast_emails()
        tasks.prepare_to_send_ca_texts()
        utils.send_daily_report()
