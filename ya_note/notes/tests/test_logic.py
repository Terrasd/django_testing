from http import HTTPStatus
import uuid


from notes.models import Note
from notes.forms import WARNING
from .common import CommonTestCase


class TestRoutes(CommonTestCase):
    def test_user_can_create_note(self):
        url = self.get_add_note_url()
        response = self.author_client.post(url, data={
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'new-slug'
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.first()
        self.assertEqual(new_note.title, 'Заголовок')
        self.assertEqual(new_note.text, 'Текст')
        self.assertEqual(new_note.slug, 'new-slug')
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        url = self.get_add_note_url()
        response = self.client.post(url, data={
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'new-slug'
        })
        expected_url = self.get_login_url() + f'?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_not_unique_slug(self):
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
            slug='existing-slug'
        )
        url = self.get_add_note_url()
        response = self.author_client.post(url, data={
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'existing-slug'
        })
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 2)

    def test_empty_slug(self):
        url = self.get_add_note_url()
        response = self.author_client.post(url, data={
            'title': 'Заголовок',
            'text': 'Текст',
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, self.get_success_url())
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.first()
        expected_slug = 'new-slug'
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_delete_note(self):
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
            slug=str(uuid.uuid4())[:8]
        )
        url = self.get_delete_note_url(self.note.slug)
        response = self.author_client.post(url)
        self.assertRedirects(response, self.get_success_url())
        self.assertEqual(Note.objects.count(), 1)

    def test_other_user_cant_delete_note(self):
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = self.get_delete_note_url(self.note.slug)
        response = self.auth_user_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_can_edit_note(self):
        self.note = Note.objects.create(
            title='Измененный заголовок',
            text='Измененный текст',
            author=self.author,
        )
        url = self.get_edit_note_url(self.note.slug)
        response = self.author_client.post(url, data={
            'title': 'Измененный заголовок',
            'text': 'Измененный текст',
            'slug': 'new-slug'
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Измененный заголовок')
        self.assertEqual(self.note.text, 'Измененный текст')
        self.assertEqual(self.note.slug, 'izmenennyij-zagolovok')

    def test_other_user_cant_edit_note(self):
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = self.get_edit_note_url(self.note.slug)
        response = self.auth_user_client.post(url, data={
            'title': 'Измененный заголовок',
            'text': 'Измененный текст',
            'slug': 'new-slug'
        })
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
