import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache

from ..models import Group, Post, Comment, Follow
from ..forms import PostForm
from ..views import POSTS_ON_PAGE

User = get_user_model()
POSTS_ON_LAST_PAGE = 3

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.count_posts = POSTS_ON_PAGE + POSTS_ON_LAST_PAGE
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост14',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует правильный шаблон."""
        self.post = Post.objects.create(
            author=PostPagesTests.user,
            text='Тестовый пост',
            group=PostPagesTests.group,
        )
        template_pages = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': '1'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': '1'}
            ): 'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
        }
        for reverse_name, template in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_first_page_contains_10_records_and_correct_context(self):
        """Паджинатор выводит на странице N постов и Post в контексте."""
        self.posts_obj = [
            Post(
                author=PostPagesTests.user,
                text='Тестовый пост',
                group=PostPagesTests.group,
            )
            for _ in range(PostPagesTests.count_posts)
        ]
        Post.objects.bulk_create(self.posts_obj)
        pagination_pages = {
            reverse('posts:index'): POSTS_ON_PAGE,
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ): POSTS_ON_PAGE,
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            ): POSTS_ON_PAGE,
        }
        for reverse_name, count_posts in pagination_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                # проверка паджинатора
                context = response.context['page_obj'].object_list
                self.assertEqual(
                    len(response.context['page_obj']),
                    count_posts
                )
                # проверка передачи в контексте Post'а
                first_object = context[0]
                self.assertEqual(first_object.__class__, Post)

    def test_group_list_page_contains_correct_other_context(self):
        """В шаблон group_list передается правильный доп. контекст."""
        response = (self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ))
        )
        group = response.context['group']
        self.assertEqual(group, PostPagesTests.group)

    def test_profile_page_contains_correct_other_context(self):
        """В шаблон profile передается правильный доп. контекст."""
        response = (self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            ))
        )
        author = response.context['author']
        self.assertEqual(str(author), 'auth')

    def test_second_page_contains_n_records(self):
        """Паджинатор выводит правильно оставшиеся посты."""
        self.posts_obj = [
            Post(
                author=PostPagesTests.user,
                text='Тестовый пост',
                group=PostPagesTests.group,
            )
            for _ in range(PostPagesTests.count_posts)
        ]
        Post.objects.bulk_create(self.posts_obj)
        pagination_pages = {
            reverse('posts:index'): POSTS_ON_LAST_PAGE,
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                POSTS_ON_LAST_PAGE,
            reverse('posts:profile', kwargs={'username': 'auth'}):
                POSTS_ON_LAST_PAGE,
        }
        for reverse_name, count_posts in pagination_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse_name + '?page=2'
                )
                self.assertEqual(
                    len(response.context['page_obj']),
                    POSTS_ON_LAST_PAGE + 1
                )

    def test_post_detail_page_contains_correct_context(self):
        """В шаблон post_detail передается правильный контекст."""
        posts_author_count = 1
        self.user = User.objects.create_user(username='other_auth')
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост 14'
        )
        response = (self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ))
        )
        post = response.context['post']
        count = response.context['count']
        self.assertEqual(post, self.post)
        self.assertEqual(count, posts_author_count)

    def test_edit_and_create_pages_contains_correct_context(self):
        """Шаблон post_create и post_edit содержит правильный контекст."""
        self.post = Post.objects.create(
            author=PostPagesTests.user,
            text='Тестовый пост',
            group=PostPagesTests.group,
        )
        pages_with_forms = {
            reverse(
                'posts:post_edit',
                kwargs={'post_id': '1'}
            ): True,
            reverse('posts:post_create'): False,
        }
        for reverse_name, is_edit in pages_with_forms.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIsInstance(response.context['form'], PostForm)
                self.assertEqual(response.context['is_edit'], is_edit)

    def test_extended_verification_add_with_group(self):
        """Расширенная проверка обработки поста с добавленной группой"""
        self.group = Group.objects.create(
            title='Другая тестовая группа',
            slug='other-test-slug',
            description='Другое тестовое описание',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост 14',
            group=self.group
        )
        template_pages = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'other-test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            ): 'posts/profile.html',
        }
        for reverse_name, template in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                context = response.context['page_obj'].object_list
                self.assertIn(self.post, context)

        # проверка, что пост с группой не попал в другую группу
        response = (self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ))
        )
        context = response.context['page_obj'].object_list
        self.assertNotIn(self.post, context)

    def test_context_with_image(self):
        """Передача изображения в контексте"""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.user = User.objects.create_user(username='other_auth')
        self.group = Group.objects.create(
            title='Другая тестовая группа',
            slug='other-test-slug',
            description='Другое тестовое описание',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост14',
            group=self.group,
            image=self.uploaded
        )
        pages_with_images = {
            reverse('posts:index'): 'page_obj',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'page_obj',
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ): 'page_obj',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'post',
        }
        for reverse_name, cont in pages_with_images.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                if cont != 'post':
                    context = response.context[cont]
                    self.assertIn(self.post, context)
                else:
                    context = response.context[cont]
                    self.assertEqual(self.post, context)

    def test_post_detail_page_comments(self):
        """В шаблон post_detail передается комментарии."""
        self.user = User.objects.create_user(username='other_auth')
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост14',
        )
        self.comment = Comment.objects.create(
            author=self.user,
            text='Тестовый комментарий',
            post=self.post
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.pk}
                    )
        )
        comments = response.context['comments']
        self.assertIn(self.comment, comments)

    def test_index_page_cache(self):
        """Кэширование index_page."""
        self.user = User.objects.create_user(username='other_auth')
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост14',
        )
        response = self.client.get(reverse('posts:index'))
        context = response.context['page_obj'].object_list
        self.assertIn(self.post, context)
        self.post.delete()

        # после удаления поста, response в кэше и повторно не возвращается
        response = self.client.get(reverse('posts:index'))
        self.assertTrue(response.context is None)
        cache.clear()

        # после очистки кэша, response возвращает новый результат
        response = self.client.get(reverse('posts:index'))
        context = response.context['page_obj'].object_list
        self.assertNotIn(self.post, context)

    def test_follow_author(self):
        """Подписка на автора доступна."""
        self.user = User.objects.create_user(username='other_auth')
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user})
        )
        context = response.context['following']
        self.assertFalse(context)

    def test_unfollow_author(self):
        """Удаление подписки на автора возможно."""
        self.user = User.objects.create_user(username='other_auth')
        self.follow = Follow.objects.create(
            user=PostPagesTests.user,
            author=self.user
        )
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user})
        )
        context = response.context['following']
        self.assertTrue(context)

    def test_follow_index_page(self):
        """Проверка вывода Post на странице подписок."""
        self.user = User.objects.create_user(username='other_auth')
        self.follow = Follow.objects.create(
            user=self.user,
            author=PostPagesTests.user
        )
        # Пост у посетителя, не подписанного на автора не выводиться.
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        follow_posts_count = len(response.context['page_obj'])
        self.assertIs(follow_posts_count, 0)

        # Пост у посетителя, подписанного на автора выводиться.
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        follow_posts_count = len(response.context['page_obj'])
        self.assertIs(follow_posts_count, 1)
