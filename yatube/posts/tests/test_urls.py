from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.cache import cache

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 12345',
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_posts_public_url(self):
        """Проверка общедоступных страниц."""
        public_pages = {
            'index': '/',
            'group_list': '/group/test-slug/',
            'profile': '/profile/auth/',
            'post_detail': '/posts/1/',
        }
        for name, path in public_pages.items():
            with self.subTest(name_page=name):
                self.assertEqual(
                    self.guest_client.get(path).status_code,
                    HTTPStatus.OK
                )

    def test_posts_authorized_url(self):
        """Проверка страниц доступных только авторизованным клиентам."""
        other_user = User.objects.create_user(username='other_auth')
        self.authorized_client.force_login(other_user)
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_author_url(self):
        """Проверка страниц доступных только авторам."""
        self.authorized_client.force_login(PostURLTests.user)
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_redirect_anonymous(self):
        """Перенаправление анонимного пользователя."""
        redirect_pages = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
        }
        for path, redirect in redirect_pages.items():
            with self.subTest(path=path):
                response = self.guest_client.get(path, follow=True)
                self.assertRedirects(response, redirect)

    def test_posts_url_redirect_authorized_non_author(self):
        """Перенаправление авторизованных клиентов."""
        other_user = User.objects.create_user(username='other_auth')
        self.authorized_client.force_login(other_user)
        response = self.authorized_client.get(
            '/posts/1/edit/',
            follow=True
        )
        self.assertRedirects(response, '/posts/1/')

    def test_page_not_found(self):
        """Проверка на код 404."""
        response = self.guest_client.get('/err_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_uses_correct_template(self):
        """Проверка на использование верных шаблонов Post."""
        self.authorized_client.force_login(PostURLTests.user)
        template_pages = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/post_create.html',
            '/posts/1/edit/': 'posts/post_create.html',
        }
        for path, template in template_pages.items():
            with self.subTest(path=path):
                response = self.authorized_client.get(path)
                self.assertTemplateUsed(response, template)
