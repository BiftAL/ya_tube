from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 12345',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        len_text = 15
        group = PostModelTest.group
        post = PostModelTest.post
        self.assertEqual(str(group), group.title)
        self.assertEqual(str(post), post.text[:len_text])

    def test_verbose_name_group(self):
        """verbose_name в полях group совпадает с ожидаемым."""
        group = PostModelTest.group
        group_field_verboses = {
            'title': 'Заголовок',
            'slug': 'Имя ссылки',
            'description': 'Описание',
        }
        for field, expected_value in group_field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_verbose_name_post(self):
        """verbose_name в полях post совпадает с ожидаемым."""
        post = PostModelTest.post
        post_field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in post_field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text_group(self):
        """help_text в полях group совпадает с ожидаемым."""
        group = PostModelTest.group
        field_help_texts = {
            'description': 'Описание группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text,
                    expected_value
                )

    def test_help_text_post(self):
        """help_text в полях post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value
                )
