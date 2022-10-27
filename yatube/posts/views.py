from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginator_func


def index(request):
    """Генерация данных для главной страницы"""
    index_list = Post.objects.all().select_related('group', 'author')
    context = {
        'page_obj': paginator_func(index_list, request)
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Генерация данных для страницы с постами группы"""
    group = get_object_or_404(Group, slug=slug)
    group_list = group.posts.all().select_related('author')
    context = {
        'group': group,
        'page_obj': paginator_func(group_list, request)
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Генерация данных для страницы с постами автора"""
    author = get_object_or_404(User, username=username)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author
    ).exists()
    profile_list = author.posts.all().select_related('group')
    context = {
        'author': author,
        'page_obj': paginator_func(profile_list, request),
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Генерация данных для страницы выбранного поста"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создаем новый пост"""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', username=new_post.author)
    return render(request, "posts/create_post.html", {'form': form})


@login_required
def post_edit(request, post_id):
    """Вносим изменнения в ранее созданный пост"""
    edit_post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edit_post
    )
    if request.user != edit_post.author:
        return redirect('posts:post_detail', post_id=post_id)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
    context = {'form': form, 'is_edit': True}
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    """Добавляем комментарий к посту"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Генерация данных для страницы с подписками"""
    follow_posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related('group')
    context = {
        'page_obj': paginator_func(follow_posts, request)
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписываемся на автора"""
    author = get_object_or_404(User, username=username)
    if author != request.user and not Follow.objects.filter(
            user=request.user, author=author).exists():
        Follow.objects.create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """Отписываемся от автора"""
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=request.user,
        author=author
    )
    if follow.exists():
        follow.delete()
    return redirect('posts:profile', username)
