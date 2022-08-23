from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма добавления нового поста с использованием модели Post."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Картинка'
        }
        help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Картинка для привлечения внимания'
        }
        # Я добавил label и help_text, но мне кажется это избыточно,
        # поскольку в модели, присутствует verbose_name и help_text.


class CommentForm(forms.ModelForm):
    """Форма добавления нового комментария использует модель Comment."""

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Текст комментария'}
        help_texts = {'text': 'Введите текст комментария'}
