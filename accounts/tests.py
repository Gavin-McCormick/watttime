from django.test import TestCase
from django.core import mail
import datetime
import settings
from accounts import models, regions, twilio_utils, forms, views

email = (lambda i : 'user{:d}@example.com'.format(i))
class AccountsTest(TestCase):
    def setUp(self):
        # Create some users
        self.user1 = views.create_new_user(email(1), 'User 1', 'CA')
        self.user2 = views.create_new_user(email(2), state = 'MA')
        self.user3 = views.create_new_user(email(3))

    def test_regions(self):
        # Test the existence of regions, the ability to create new regions,
        # and the ability to relate a state to a region.
        ## There should be 3 regions: CA, NE, and null
        self.assertEqual(len(regions.regions), 3)
        for region in regions.regions:
            self.assertIsInstance(region, regions.Region)

        test_region = regions.Region('Test', 'nonexistent', ['TX', 'FL'], [regions.ConfigBoolean('test_bool')])

        ## Now there should be 4 regions
        self.assertEqual(len(regions.regions), 4)
        for region in regions.regions:
            self.assertIsInstance(region, regions.Region)

        self.assertIs(regions.state_to_region('CA'), regions.california)
        self.assertIs(regions.state_to_region('MA'), regions.newengland)
        self.assertIs(regions.state_to_region('TX'), test_region)
        self.assertIs(regions.state_to_region('NC'), regions.null_region)
        self.assertTrue(regions.california.has_state('CA'))
        self.assertTrue(test_region.has_state('FL'))
        self.assertFalse(regions.california.has_state('FL'))
        self.assertFalse(test_region.has_state('CA'))

        # Test relationships between form fields and model fields
        # Ideally I should test the ability to save to-from the database
        # but that would require creating a new table here dynamically!
        c1 = regions.ConfigMultichoice('c1', [('a', 'A'), ('b', 'B')])
        self.assertEqual(c1.form_to_model([]), '')
        self.assertEqual(c1.form_to_model(['1']), '1')
        self.assertEqual(c1.form_to_model(['0', '1']), '0,1')
        self.assertEqual(c1.model_to_form(''), [])
        self.assertEqual(c1.model_to_form('0,1'), ['0', '1'])
        self.assertEqual(c1.model_to_display(''), '(none)')
        self.assertEqual(c1.model_to_display('0,1'), 'a; b')

        c2 = regions.ConfigChoice('c2', [('a', 'A'), ('b', 'B')])
        self.assertEqual(c2.form_to_model('0'), 0)
        self.assertEqual(c2.model_to_form(0), '0')
        self.assertEqual(c2.model_to_display('0'), 'a')

    def test_user_creation(self):
        emails = []
        for up in models.UserProfile.objects.all():
            emails.append(up.email)
        emails.sort()
        self.assertEqual(emails, [email(1), email(2), email(3)])

        self.assertIsNone(views.create_new_user(email(1)))
        self.assertIsNone(views.create_new_user(email(2)))

        user4 = views.create_new_user(email(4))

        for user in [self.user1, self.user2, self.user3, user4]:
            self.assertIsNotNone(user)
            self.assertFalse(user.is_active)
            self.assertFalse(user.is_staff)
            self.assertFalse(user.is_superuser)

            up = user.get_profile()
            self.assertEqual(up.phone, '')
            self.assertFalse(up.is_verified)
            self.assertIs(user, up.user)
            self.assertFalse(up.password_is_set)
            self.assertIsNotNone(up.get_region_settings())
            self.assertIsNotNone(up.region())
            self.assertIsInstance(str(up), str)
            self.assertIsInstance(up.long_state_name(), str)
            self.assertIsInstance(up.local_now(), datetime.datetime)

        self.assertEqual(len(mail.outbox), 0)
        views.create_and_email_user(email(5))
        self.assertEqual(len(mail.outbox), 1)
        views.create_and_email_user(email(2))
        self.assertEqual(len(mail.outbox), 1)

        m = mail.outbox[0]
        self.assertEqual(m.to, [email(5)])
        self.assertEqual(m.from_email, settings.EMAIL_HOST_USER)

