from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug'
        )

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_create_post_authorized_client(self):
        """Проверяем что пост создается авторизованным пользователем"""
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), 1)
        new_post = Post.objects.first()
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group, self.group)
        self.assertEqual(new_post.author, self.user)

    def test_create_post_guest_client(self):
        """Проверяем что пост не создается не авторизованным пользователем"""
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), 0)
        self.assertRedirects(
            response,
            f'{reverse("users:login")}'
            f'?next={reverse("posts:post_create")}'
        )

    def test_edit_post_authorized_client(self):
        """Авторизованный пользователь может изменить свой пост"""
        self.post = Post.objects.create(
            text='Текст поста',
            group=self.group,
            author=self.user
        )
        form_data = {
            'text': 'Внесли изменения в текст поста',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post_edit = Post.objects.first()
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.author, self.post.author)
        self.assertEqual(post_edit.group, self.group)

    def test_edit_post_guest_client(self):
        """Неавторизованный пользователь не может отредактировать пост"""
        self.post = Post.objects.create(
            text='Текст поста',
            group=self.group,
            author=self.user,
        )
        form_data = {
            'text': 'Внесли изменения в текст поста'
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, f'{reverse("users:login")}'
            f'?next='
            f'{reverse("posts:post_edit", kwargs={"post_id": self.post.id})}'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
