import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
@pytest.mark.usefixtures('news_data')
def test_news_count(client):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('news_data')
def test_news_order(client):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('comments_data')
def test_comments_order(client, news):
    response = client.get(reverse('news:detail', args=(news.pk,)))
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_context, is_instance',
    (
        (pytest.lazy_fixture('author_client'), True, True),
        (pytest.lazy_fixture('client'), False, False),
    ),
)
def test_form_for_auth_and_anonymous_users(
    parametrized_client, form_in_context, is_instance, news
):
    response = parametrized_client.get(reverse('news:detail', args=(news.pk,)))
    assert ('form' in response.context) is form_in_context
    assert isinstance(response.context.get('form'), CommentForm) is is_instance
