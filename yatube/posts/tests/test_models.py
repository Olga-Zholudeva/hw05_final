from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    def setUp(self):
        super().setUpClass()
        self.user = User.objects.create_user(
            username='test_user'
        )
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестируем работает ли ограченние в str на вывод',
        )

    def test_models_have_correct_object_names(self):
        field_str = {
            len(self.post.text[:15]): len(str(self.post)),
            self.group.title: str(self.group)
        }
        for field, value in field_str.items():
            with self.subTest(field=field):
                self.assertEqual(field, value)
