from django.core.management import base
from accounts.models import UserProfile
import csv


class Command(base.BaseCommand):
    help = 'Export contact list of active users'

    def handle(self, *args, **kwargs):
        # create csv writer to stdout
        writer = csv.writer(self.stdout)

        # add header
        writer.writerow(['EMAIL', 'FIRST NAME', 'LAST NAME',
                         'PHONE', 'STATE', 'PHONE_VERIFIED'])

        for up in UserProfile.objects.filter(user__is_active=True):
            # try to get first and last name
            name_pieces = up.name.split()
            if len(name_pieces) > 1:
                fname = name_pieces[0]
                lname = ' '.join(name_pieces[1:])
            else:
                fname = up.name
                lname = None

            # write row
            writer.writerow([up.email, fname, lname,
                             up.phone, up.state, up.is_verified])
