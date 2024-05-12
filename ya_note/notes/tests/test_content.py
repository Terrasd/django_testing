from django.contrib.auth import get_user_model

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
                object_list = response.context.get('object_list', [])
                if note_in_list:
                    self.assertIn(self.note, object_list)

                    note_from_list = next((note for note in object_list
                                           if note.pk == self.note.pk), None)
                    self.assertIsNotNone(note_from_list)
                    self.assertEqual(note_from_list.title, self.note.title)
                    self.assertEqual(note_from_list.text, self.note.text)
                    self.assertEqual(note_from_list.author, self.note.author)
                else:
                    self.assertNotIn(self.note, object_list)

    def test_notes_list_for_unauthenticated_user(self):
        response = self.client.get(self.get_notes_list_url())
        self.assertRedirects(response,
                             f'{self.get_login_url()}'
                             + f'?next={self.get_notes_list_url()}')

    def test_pages_contains_form(self):
        for name, args in (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        ):
            with self.subTest():
                url = (self.get_add_note_url()
                       if not args else self.get_edit_note_url(self.note.slug))
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                form_class = response.context['form'].__class__
                self.assertEqual(form_class, NoteForm)
