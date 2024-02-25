from datetime import timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='author')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='not author')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(title='title', text='text')


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='text',
    )


@pytest.fixture
def news_data():
    now = timezone.now()
    News.objects.bulk_create(
        News(
            title=f'News {index}',
            text='Just text.',
            date=now.date() + timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments_data(news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Text {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def comments_count():
    return Comment.objects.count()
