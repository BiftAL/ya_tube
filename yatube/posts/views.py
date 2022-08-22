from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .models import Post, Group, Follow, User
from .forms import PostForm, CommentForm

POSTS_ON_PAGE = 10
CACHING_TIME = 20


@cache_page(CACHING_TIME, key_prefix='index_page')
def index(request: any) -> render:
    """Главная страница учебного проекта."""
    template_name = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group').all()
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


def group_posts(request: any, slug: any) -> render:
    """Страница отображающая сообщения группы переданной в параметрах."""
    template_name = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts_in_group.select_related('author', 'group').all()
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


def profile(request, username):
    """Страница отображающая профиль автора."""
    template_name = 'posts/profile.html'
    author = get_object_or_404(User, username__contains=username)
    posts = author.posts.select_related('author', 'group').all()
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=author)
    else:
        following = False
    count = author.posts.all().count()
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_count': count,
        'following': following
    }
    return render(request, template_name, context)


def post_detail(request, post_id):
    """Страница отображающая с деталями сообщения."""
    template_name = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.select_related('author', 'post').all()
    count = Post.objects.filter(author__username__contains=post.author).count()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'count': count,
        'form': form,
        'comments': comments
    }
    return render(request, template_name, context)


@login_required
def post_create(request):
    """Страница для создания нового поста."""
    template_name = 'posts/post_create.html'
    is_edit = False
    form = PostForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user)

    form = PostForm()
    context = {
        'form': form,
        'is_edit': is_edit
    }
    return render(request, template_name, context)


@login_required
def post_edit(request, post_id):
    """Страница для редактирования поста."""
    template_name = 'posts/post_create.html'
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True

    # проверка, является ли авторизованный пользователь автором поста
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'is_edit': is_edit
    }
    return render(request, template_name, context)


@login_required
def add_comment(request, post_id):
    """Страница добавления комментария к посту."""
    template_name = 'posts:post_detail'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(template_name, post_id=post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    """Главная страница учебного проекта."""
    template_name = 'posts/index.html'
    follow = (Follow.objects.select_related('author')
              .filter(user__exact=request.user))
    follow_list = [obj.author for obj in follow]
    posts = (Post.objects.select_related('author', 'group')
             .filter(author__in=follow_list))
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    template_name = 'posts:profile'
    author = get_object_or_404(User, username__contains=username)
    count_follow = Follow.objects.filter(author=author, user=request.user).count()
    print(count_follow)
    if author.pk != request.user.pk and count_follow == 0:
        print(username)
        print(request.user)
        Follow.objects.create(user=request.user, author=author)
    return redirect(template_name, author)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    template_name = 'posts:profile'
    author = get_object_or_404(User, username__contains=username)
    unfollow = Follow.objects.filter(user=request.user, author=author)
    unfollow.delete()
    return redirect(template_name, author)
