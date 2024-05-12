from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
def test_pages_availability(client, all_urls):
    for name, url in all_urls.items():
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_page(client, news, detail_url_news):
    url = detail_url_news
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, expected_status, name, comment,
        url_name_args
):
    url = url_name_args
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(client, all_urls, name, comment,
                                       url_name_args):
    login_url = all_urls['login']
    url = url_name_args
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
