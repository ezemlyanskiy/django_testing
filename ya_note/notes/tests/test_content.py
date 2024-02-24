from django.contrib.auth import get_user_model
from django.test import TestCase

from notes.forms import NoteForm

from .mixins import SetUpTestDataMixin

User = get_user_model()


class TestContent(SetUpTestDataMixin, TestCase):
    def test_notes_list_for_different_users(self):
        for user_client, note_in_list in (
            (self.author_client, True),
            (self.reader_client, False),
        ):
            with self.subTest():
                response = user_client.get(self.list_url)
                object_list = response.context['object_list']
                self.assertTrue((self.note in object_list) is note_in_list)

    def test_pages_contain_form(self):
        for url in (
            self.add_url,
            self.edit_url,
        ):
            with self.subTest():
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
