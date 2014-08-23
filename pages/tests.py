from django.test import TestCase
from django.core.urlresolvers import reverse_lazy
from pages.models import Article
from datetime import date


class ContactTest(TestCase):
    def test_contact(self):
        # send mail
        self.client.post('/contact',
                data = {
                    'subject' : 'Test subject',
                    'email' : 'example@example.com',
                    'message' : 'Test message body',
                    'name' : 'Test name'})


class TestArticle(TestCase):
    def setUp(self):
        self.data1 = {
            'published_on': date(2014,1,1),
            'title': 'someone said a thing',
            'outlet': 'fancy newspaper',
            'link': 'http://example.com/a/',  
        }

        self.data2 = {
            'published_on': date(2013,1,1),
            'title': 'a thing someone said before',
            'outlet': 'less fancy newspaper',
            'link': 'http://example.com/b/',  
        }

    def test_create(self):
        a = Article.objects.create(**self.data1)
        self.assertIsNotNone(a.published_on)
        self.assertIsNotNone(a.outlet)
        self.assertIsNotNone(a.title)
        self.assertIsNotNone(a.link)

    def test_order_by_date(self):
        a1 = Article.objects.create(**self.data1)
        a2 = Article.objects.create(**self.data2)
        self.assertEqual(Article.objects.earliest(), a2)
        self.assertEqual(Article.objects.latest(), a1)
