from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url(self):
        """Тестирование статичных страниц."""
        static_pages = {
            'author': '/about/author/',
            'tech': '/about/tech/',
        }
        for name, path in static_pages.items():
            with self.subTest(field=name):
                self.assertEqual(
                    self.guest_client.get(path).status_code,
                    HTTPStatus.OK
                )

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для адресов /about/...."""
        static_pages = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for path, template in static_pages.items():
            with self.subTest(path=path):
                response = self.guest_client.get(path)
                self.assertTemplateUsed(response, template)

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени static_pages:about, доступен."""
        static_pages = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): '/about/tech/.html',
        }
        for reverse_name, template in static_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_uses_correct_template(self):
        """При запросе about применяются правильные шаблоны."""
        static_pages = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in static_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
