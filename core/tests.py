from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_page_returns_200(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_header_has_call_to_action(self):
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'href="tel:')


class BlogPageTests(TestCase):
    def test_blog_page_returns_200(self):
        response = self.client.get(reverse('core:blog'))
        self.assertEqual(response.status_code, 200)
