from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .mixins import SetUpTestDataMixin

User = get_user_model()


class TestRoutes(SetUpTestDataMixin, TestCase):
    def test_pages_availability_for_anonymous_user(self):
        for name in (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        ):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_users(self):
        for url in (
            self.list_url,
            self.add_url,
            self.success_url,
        ):
            with self.subTest():
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        clients_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for client, status in clients_statuses:
            for url in (
                self.edit_url,
                self.detail_url,
                self.delete_url,
            ):
                with self.subTest():
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        for url in (
            self.edit_url,
            self.detail_url,
            self.delete_url,
            self.list_url,
            self.add_url,
            self.success_url,
        ):
            with self.subTest():
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
