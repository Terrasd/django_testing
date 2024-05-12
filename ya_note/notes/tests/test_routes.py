from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .common import CommonTestCase

User = get_user_model()


class TestRoutes(CommonTestCase):
    def test_pages_availability_for_anonymous_user(self):
        urls = (
            self.get_home_url(),
            self.get_login_url(),
            self.get_logout_url(),
            self.get_signup_url(),
        )
        for url in urls:
            with self.subTest():
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            self.get_notes_list_url(),
            self.get_success_url(),
            self.get_add_note_url(),
        )
        for url in urls:
            with self.subTest():
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        urls = (
            self.get_detail_note_url(self.note.slug),
            self.get_edit_note_url(self.note.slug),
            self.get_delete_note_url(self.note.slug),
        )
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.auth_user_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for url in urls:
                with self.subTest(user=user, url=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        login_url = self.get_login_url()
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest():
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
