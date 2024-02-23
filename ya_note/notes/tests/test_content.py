from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='test title',
            text='test text',
            slug='test-slug',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        for user_client, note_in_list in (
            (self.author_client, True),
            (self.reader_client, False),
        ):
            with self.subTest():
                url = reverse('notes:list')
                response = user_client.get(url)
                object_list = response.context['object_list']
                self.assertTrue((self.note in object_list) is note_in_list)

    def test_pages_contain_form(self):
        for name, args in (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        ):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
