from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(UserURLTests.user)

    def test_users_public_url(self):
        """Проверка общедоступных страниц."""
        public_pages = {
            'signup': '/auth/signup/',
            'login': '/auth/login/',
            'password_reset_form': '/auth/password_reset/',
            'password_reset_done': '/auth/password_reset/done/',
            'password_reset_complete': '/auth/reset/done/',
        }
        for name, path in public_pages.items():
            with self.subTest(name_page=name):
                self.assertEqual(
                    self.guest_client.get(path).status_code,
                    HTTPStatus.OK
                )

    def test_users_authorized_url(self):
        """Проверка страниц для авторизованных клиентов."""
        auth_pages = {
            'password_change_form': '/auth/password_change/',
            'password_change_done': '/auth/password_change/done/',
        }
        for name, path in auth_pages.items():
            with self.subTest(name_page=name):
                self.assertEqual(
                    self.authorized_client.get(path).status_code,
                    HTTPStatus.OK
                )

    def test_users_url_redirect_anonymous(self):
        """Перенаправление анонимного пользователя."""
        redirect_pages = {
            '/auth/password_change/':
                '/auth/login/?next=/auth/password_change/',
            '/auth/password_change/done/':
                '/auth/login/?next=/auth/password_change/done/',
        }
        for path, redirect in redirect_pages.items():
            with self.subTest(path=path):
                response = self.guest_client.get(path, follow=True)
                self.assertRedirects(response, redirect)

    def test_url_uses_correct_template(self):
        """Проверка на использование верных шаблонов User."""
        template_pages = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for path, template in template_pages.items():
            with self.subTest(path=path):
                response = self.authorized_client.get(path)
                self.assertTemplateUsed(response, template)
