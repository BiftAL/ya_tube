from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import CreationForm

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.form = CreationForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в User."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'username': 'test_test',
            'email': 'test@test.test',
            'password1': 'pa$$word123',
            'password2': 'pa$$word123'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='first_name',
                last_name='last_name',
                username='test_test',
                email='test@test.test'
            ).exists()
        )
