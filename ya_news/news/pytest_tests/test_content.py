import pytest

from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, list_news, all_urls):
    url = all_urls['home']
    response = client.get(url)
    assert 'object_list' in response.context, (
        'Отсутствует ключ "bject_list" в контексте ответа')
    object_list = response.context.get('object_list', [])
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, list_news, all_urls):
    url = all_urls['home']
    response = client.get(url)
    object_list = response.context['object_list']
    sorted_news = sorted(list_news, key=lambda x: x.date, reverse=True)

    object_list_data = [{'title': news_data.title, 'date': news_data.date}
                        for news_data in object_list]
    sorted_news_data = [{'title': news_data.title,
                         'date': news_data.date.date()}
                        for news_data in sorted_news]

    assert object_list_data == sorted_news_data


@pytest.mark.django_db
def test_comments_order(client, news, list_comments, detail_url_news):
    url = detail_url_news
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']

    all_comments = news.comment_set.order_by('created').all()
    for i in range(len(all_comments) - 1):
        assert all_comments[i].created < all_comments[i + 1].created


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
@pytest.mark.django_db
def test_comment_form_access_for_anonymous_client(parametrized_client,
                                                  status, detail_url_comm):
    url = detail_url_comm
    response = parametrized_client.get(url)
    assert ('form' in response.context) is status


@pytest.mark.django_db
def test_correct_comment_form_passed_to_template(author_client,
                                                 detail_url_news):
    url = detail_url_news
    response = author_client.get(url)
    assert 'form' in response.context
    comment_form = response.context['form']
    assert isinstance(comment_form, CommentForm)
