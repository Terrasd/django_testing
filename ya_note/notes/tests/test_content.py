from django.contrib.auth import get_user_model
from django.urls import reverse

from .common import CommonTestCase
from notes.forms import NoteForm

User = get_user_model()


class TestRoutes(CommonTestCase):
    def test_notes_list_for_different_users(self):
        for user, note_in_list in (
                (self.author_client, True), (self.auth_user_client, False)):
            with self.subTest():
                url = self.get_notes_list_url()
                response = user.get(url)
                object_list = response.context['object_list']
                if note_in_list:
                    self.assertIn(self.note, object_list)

                    note_from_list = object_list.get(pk=self.note.pk)
                    self.assertEqual(note_from_list.title, self.note.title)
                    self.assertEqual(note_from_list.text, self.note.text)
                    self.assertEqual(note_from_list.author, self.note.author)
                else:
                    self.assertNotIn(self.note, object_list)

    def test_notes_list_for_unauthenticated_user(self):
        url = self.get_notes_list_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        expected_url = reverse('users:login') + f'?next={url}'
        self.assertEqual(response.url, expected_url)

    def test_pages_contains_form(self):
        for name, args in (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        ):
            with self.subTest():
                url = (self.get_edit_note_url(self.note.slug) if
                       args else self.get_add_note_url())
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                form_class = response.context['form'].__class__
                self.assertEqual(form_class, NoteForm)
