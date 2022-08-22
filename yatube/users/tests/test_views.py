from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms


User = get_user_model()


class UserPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(UserPagesTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует правильный шаблон users."""
        template_pages = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
        }
        for reverse_name, template in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_user_pages_contains_correct_context(self):
        """В шаблон users:signup в контексте передаётся форма."""
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.CharField
        }
        response = self.guest_client.get(reverse('users:signup'))
        # Проверяем, что типы полей формы в словаре context соответствуют
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = (
                    response.context['form'].fields[value]
                )
                self.assertIsInstance(form_field, expected)

    def test_login_user_pages_contains_correct_context(self):
        """В шаблон users:login в контексте передаётся форма."""
        form_fields = {
            'username': forms.fields.CharField,
            'password': forms.fields.CharField
        }
        response = self.guest_client.get(reverse('users:login'))
        # Проверяем, что типы полей формы в словаре context соответствуют
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = (
                    response.context['form'].fields[value]
                )
                self.assertIsInstance(form_field, expected)
