from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

from .mixins import SetUpTestDataMixin

User = get_user_model()


class TestLogic(SetUpTestDataMixin, TestCase):
    NEW_TITLE = 'new title'
    NEW_TEXT = 'new text'
    NEW_SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        SetUpTestDataMixin.setUpTestData()
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
            'slug': cls.NEW_SLUG,
        }
        cls.old_count = Note.objects.count()

    def test_user_can_create_note(self):
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), self.old_count + 1)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.add_url, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), self.old_count)

    def test_not_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), self.old_count)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), self.old_count + 1)
        new_note = Note.objects.all().last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def update_note(self, client, expected_url_or_404, title, text, slug):
        response = client.post(self.edit_url, data=self.form_data)

        if client == self.author_client:
            self.assertRedirects(response, expected_url_or_404)
        else:
            self.assertEqual(response.status_code, expected_url_or_404)

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, title)
        self.assertEqual(self.note.text, text)
        self.assertEqual(self.note.slug, slug)

        if client == self.author_client:
            self.note.title = self.TITLE
            self.note.text = self.TEXT
            self.note.slug = self.SLUG
            self.note.save()

    def test_author_can_edit_note(self):
        self.update_note(
            self.author_client,
            self.success_url,
            self.NEW_TITLE,
            self.NEW_TEXT,
            self.NEW_SLUG,
        )

    def test_other_user_cant_edit_note(self):
        self.update_note(
            self.reader_client,
            HTTPStatus.NOT_FOUND,
            self.TITLE,
            self.TEXT,
            self.SLUG,
        )

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), self.old_count - 1)

    def test_other_user_cant_delete_note(self):
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), self.old_count)
