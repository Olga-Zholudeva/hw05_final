from django.urls import reverse
from django.test import TestCase, Client
from http import HTTPStatus


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
        self.authorized_client2 = Client()

    def test_pages_and_template_names_for_non_authorized_users(self):
        self.guest_client = Client()
        url_addresses_templates_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/test_user/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
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
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in url_addresses_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_redirect_guest_user_fo_page_post_edit_create(self):
        self.guest_client = Client()
        url_page_redirect_address = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/'
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

    def test_request_to_a_non_existent_page(self):
        self.guest_client = Client()
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
