from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class CommonTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.auth_user = User.objects.create(username='auth_user')
        cls.auth_user_client = Client()
        cls.auth_user_client.force_login(cls.auth_user)
        cls.data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',
        }
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='new-slug',
        )

    @staticmethod
    def get_notes_list_url():
        return reverse('notes:list')

    @staticmethod
    def get_add_note_url():
        return reverse('notes:add')

    @staticmethod
    def get_edit_note_url(slug):
        return reverse('notes:edit', args=[slug])

    @staticmethod
    def get_delete_note_url(slug):
        return reverse('notes:delete', args=[slug])

    @staticmethod
    def get_home_url():
        return reverse('notes:home')

    @staticmethod
    def get_login_url():
        return reverse('users:login')

    @staticmethod
    def get_logout_url():
        return reverse('users:logout')

    @staticmethod
    def get_signup_url():
        return reverse('users:signup')

    @staticmethod
    def get_success_url():
        return reverse('notes:success')

    @staticmethod
    def get_detail_note_url(slug):
        return reverse('notes:detail', args=[slug])
