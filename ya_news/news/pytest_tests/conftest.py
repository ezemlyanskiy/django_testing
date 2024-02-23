from datetime import datetime, timedelta

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
def news_pk(news):
    return (news.pk,)


@pytest.fixture
def comment_pk(comment):
    return (comment.pk,)


@pytest.fixture
def news_data():
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'News {index}',
            text='Just text.',
            date=today - timedelta(index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    yield
    News.objects.all().delete()


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
    yield
    Comment.objects.all().delete()


@pytest.fixture
def form_data():
    return {
        'text': 'Comment text',
    }
