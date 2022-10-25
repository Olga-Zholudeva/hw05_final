from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostCachingTest(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='Test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug'
        )
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group
        )

    def test_caching_page_index(self):
        response_content = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(Post.objects.count(), 1)
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_content.content, response.content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response_content.content, response.content)
