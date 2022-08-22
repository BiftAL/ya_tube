from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма добавления нового поста с использованием модели Post."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    """Форма добавления нового комментария использует модель Comment."""

    class Meta:
        model = Comment
        fields = ('text',)
