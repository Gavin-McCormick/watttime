from django.test import TestCase
from django.core import mail
import settings

class ContactTest(TestCase):
    def test_contact(self):
        # send mail
        self.client.post('/contact',
                data = {
                    'subject' : 'Test subject',
                    'email' : 'example@example.com',
                    'message' : 'Test message body',
                    'name' : 'Test name'})

        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(len(m.to), 1)
        self.assertEqual(m.to[0], settings.EMAIL_HOST_USER)
        self.assertEqual(m.from_email, settings.EMAIL_HOST_USER)
