from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django import forms
from posts.forms import PostForm

from ..models import Group, Post, User


TEST_POST_ID = 1


class PostPegesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.templates_pages_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': TEST_POST_ID}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': TEST_POST_ID}
            ): 'posts/create_post.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_users_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_users_correct_context_with_paginator(self):
        """Проверка словаря context для страниц с паджинатором"""
        count_test_post = 18
        test_posts = []
        for i in range(count_test_post):
            test_posts.append(Post(
                author=self.user,
                group=self.group,
                text=f'Тестовый текст поста {i + 1}'))
        Post.objects.bulk_create(test_posts)
        pages = [
            reverse('posts:index'),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}),
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        ]
        for page in pages:
            respons_first_page = self.client.get(page)
            respons_second_page = self.client.get(page + '?page=2')
            self.assertEqual(
                len(respons_first_page.context['page_obj']),
                settings.LIMIT_POSTS
            )
            self.assertEqual(
                len(respons_second_page.context['page_obj']),
                count_test_post - settings.LIMIT_POSTS + 1
            )

    def test_correct_context_post_edit(self):
        """Проверка словаря context страницы post_edit"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': TEST_POST_ID}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = (
                    response.context.get('form').fields.get(value)
                )
                self.assertIsInstance(form_field, expected)
                self.assertEqual(response.context['is_edit'], True)

    def test_correct_context_post_create(self):
        """Проверка словаря context страницы post_create"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = (response.context.get('form').fields.get(value))
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_detail_pages(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': TEST_POST_ID})
        )
        get_post_context = response.context.get('post')
        test_post = {
            get_post_context.author: self.user,
            get_post_context.group: self.group,
            get_post_context.text: 'Тестовый пост',
        }
        for value, expected in test_post.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_additional_verification_when_creating_a_post(self):
        """При создании пост появляется на нужных страницах"""
        test_post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Проверочный пост',
        )
        pages = [
            reverse('posts:index'),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
        ]
        for reverse_name in pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.author, test_post.author)
                self.assertEqual(first_object.group, test_post.group)
                self.assertEqual(first_object.text, test_post.text)

    def test_post_did_not_get_into_another_group(self):
        """Пост не попал в группу, для которой не был предназначен"""
        self.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2'
        )
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.group2.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 0)
