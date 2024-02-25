from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Comment text'}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, comments_count):
    client.post(reverse('news:detail', args=(news.pk,)))
    assert Comment.objects.count() == comments_count


def test_user_can_create_comment(author, author_client, news, comments_count):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=FORM_DATA)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == comments_count + 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, comments_count):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        'form',
        'text',
        errors=WARNING,
    )
    assert Comment.objects.count() == comments_count


def test_author_can_delete_comment(
    author_client, comment, news, comments_count
):
    url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(url)
    assertRedirects(
        response, reverse('news:detail', args=(news.pk,)) + '#comments'
    )
    assert Comment.objects.count() == comments_count - 1


def test_user_cant_delete_comment_of_another_user(
    not_author_client, comment, comments_count
):
    url = reverse('news:delete', args=(comment.pk,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count


def test_author_can_edit_comment(author_client, comment, news):
    url = reverse('news:edit', args=(comment.pk,))
    response = author_client.post(url, data=FORM_DATA)
    assertRedirects(
        response, reverse('news:detail', args=(news.pk,)) + '#comments'
    )
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']


def test_user_cant_edit_comment_of_another_user(not_author_client, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = not_author_client.post(url, FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != FORM_DATA['text']
