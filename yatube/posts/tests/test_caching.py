from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache


from ..models import Group, Post, User


class PostCachingTest(TestCase):
    def test_caching_page_index(self):
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
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(Post.objects.count(), 1)
        content = response.content
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(content, response.content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(content, response.content)
