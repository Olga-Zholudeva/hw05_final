from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст'
        )

    def setUp(self):
        cache.clear()
        self.authorized_client2 = Client()

    def test_pages_and_template_names_for_non_authorized_users(self):
        self.guest_client = Client()
        url_addresses_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
        }
        for address, template in url_addresses_templates_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_pages_and_template_names_for_authorized_users(self):
        self.user = User.objects.get(username=self.user.username)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        url_addresses_templates_names = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }
        for address, template in url_addresses_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_redirect_guest_user_fo_page_post_edit_create(self):
        self.guest_client = Client()
        url_page_redirect_address = {
            reverse('posts:post_create'):
            f'{reverse("users:login")}?next={reverse("posts:post_create")}',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            f'{reverse("users:login")}'
            f'?next='
            f'{reverse("posts:post_edit", kwargs={"post_id": self.post.id})}'
        }
        for page, redirect_address in url_page_redirect_address.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, redirect_address)

    def test_redirect_authorized_client_not_author_page_post_edit(self):
        self.user = User.objects.create(username='Test_user2')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user)
        response = self.authorized_client2.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
        ))
