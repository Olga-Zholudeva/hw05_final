from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post, User


class FollowingTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slag'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст'
        )
        cls.user = User.objects.create(username='user')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_client_can_subscribe_and_unsubscribe(self):
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author})
        )
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(Follow.objects.first().author, self.post.author)
        self.assertEqual(Follow.objects.first().user, self.user)
        self.authorized_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author})
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_new_post_appears_in_the_feed(self):
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author})
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)
        self.assertEqual(
            response.context['page_obj'][0].author, self.post.author
        )
        self.assertEqual(
            response.context['page_obj'][0].group, self.post.group
        )

    def test_new_post_appears_not_in_the_feed(self):
        self.new_user = User.objects.create(username='new_user')
        self.new_authorized_client = Client()
        self.new_authorized_client.force_login(self.new_user)
        response = self.new_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 0)
