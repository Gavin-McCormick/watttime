from django.test import TestCase
from django.core.urlresolvers import reverse_lazy
from pages.models import Article, Award, Supporter
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
            'published_on': date(2013,1,1),
            'title': 'someone said a thing',
            'outlet': 'fancy newspaper',
            'link': 'http://example.com/a/',  
        }

        self.data2 = {
            'published_on': date(2014,1,1),
            'title': 'a thing someone said later',
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
        Article.objects.create(**self.data1)
        Article.objects.create(**self.data2)
        self.assertEqual(Article.objects.first(), Article.objects.latest())
        self.assertEqual(Article.objects.last(), Article.objects.earliest())


class TestAward(TestCase):
    def setUp(self):
        self.data1 = {
            'award_name': 'first place',
            'contest_name': 'a thing we won',
            'link': 'http://example.com',
        }

    def test_create(self):
        a = Award.objects.create(**self.data1)
        self.assertIsNotNone(a.award_name)
        self.assertIsNotNone(a.contest_name)
        self.assertIsNotNone(a.link)

    def test_supporters(self):
        a = Award.objects.create(**self.data1)
        self.assertEqual(a.supporters.count(), 0)
        a.supporters.create(name='someone who likes us', link='http://example.com')
        self.assertEqual(a.supporters.count(), 1)        


class TestArticleListView(TestCase):
    def setUp(self):
        Article.objects.create(**{
            'published_on': date(2014,1,1),
            'title': 'someone said a thing',
            'outlet': 'fancy newspaper',
            'link': 'http://example.com/a/',  
        })

        Article.objects.create(**{
            'published_on': date(2013,1,1),
            'title': 'a thing someone said before',
            'outlet': 'less fancy newspaper',
            'link': 'http://example.com/b/',  
        })

    def test_get_has_context(self):
        response = self.client.get(reverse_lazy('press'))
        for a in Article.objects.all():
            self.assertIn(a, response.context['object_list'])

    def test_get_has_content(self):
        response = self.client.get(reverse_lazy('press'))
        for a in Article.objects.all():
            self.assertContains(response, a.link)
            self.assertContains(response, a.outlet)
            self.assertContains(response, a.published_on.strftime('%-d %B %Y'))
            self.assertContains(response, a.title)
