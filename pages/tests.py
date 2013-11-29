from django.test import TestCase

class ContactTest(TestCase):
    def test_contact(self):
        # send mail
        self.client.post('/contact',
                data = {
                    'subject' : 'Test subject',
                    'email' : 'example@example.com',
                    'message' : 'Test message body',
                    'name' : 'Test name'})

