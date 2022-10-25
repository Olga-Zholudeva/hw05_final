from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post, User


class CommentCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст'
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_create_commetn_authorized_client(self):
        """Проверяем что комментарий создается авторизованным пользователем"""
        form_data = {
            'post': self.post,
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.first()
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post, form_data['post'])

    def test_create_commetn_guest_client(self):
        """Комментарий не создается не авторизованным пользователем"""
        form_data = {
            'post': self.post,
            'text': 'Тестовый комментарий'
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 0)
        self.assertRedirects(
            response, f'{reverse("users:login")}'
            f'?next='
            f'{reverse("posts:add_comment",kwargs={"post_id": self.post.id})}'
        )

    def test_comment_in_page_post_detail(self):
        """Проверяем что комментарий появляется на странице поста"""
        self.comment = Comment.objects.create(
            text='Текст комментария',
            post=self.post,
            author=self.user
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            response.context['comments'][0].text, self.comment.text
        )
