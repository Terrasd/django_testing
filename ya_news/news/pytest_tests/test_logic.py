import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from .conftest import NEW_TEXT_COMMENT
from news.forms import BAD_WORDS, WARNING
from news.models import Comment

BAD_WORDS_LOCAL = BAD_WORDS


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, detail_url_news):
    url = detail_url_news
    Comment.objects.all().delete()
    client.post(url, data=NEW_TEXT_COMMENT)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, news, detail_url_news):
    url = detail_url_news
    Comment.objects.all().delete()
    author_client.post(url, data=NEW_TEXT_COMMENT)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == NEW_TEXT_COMMENT['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, detail_url_news):
    bad_words_data = {
        'text': f'Какой-то текст, {BAD_WORDS_LOCAL[0]}, еще текст'}
    url = detail_url_news
    comments_count_before = Comment.objects.count()
    response = author_client.post(url, data=bad_words_data)
    comments_count_after = Comment.objects.count()
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert comments_count_after == comments_count_before


def test_author_can_delete_comment(author_client, news, comment,
                                   detail_url_news, detail_del_news):
    news_url = detail_url_news
    url_to_comments = detail_del_news

    comments_count_before_deletion = Comment.objects.count()
    response = author_client.delete(url_to_comments)
    assertRedirects(response, news_url + '#comments')

    comments_count_after_deletion = Comment.objects.count()
    assert comments_count_after_deletion == comments_count_before_deletion - 1

    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_user_cant_delete_comment_of_another_user(admin_client, comment,
                                                  detail_del_news):
    comment_url = detail_del_news

    comments_count_before_deletion = Comment.objects.count()
    comment_before_deletion = Comment.objects.get(pk=comment.pk)
    response = admin_client.delete(comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comments_count_after_deletion = Comment.objects.count()
    assert comments_count_after_deletion == comments_count_before_deletion

    comment_after_deletion = Comment.objects.get(pk=comment.pk)
    assert comment_before_deletion.text == comment_after_deletion.text
    assert comment_before_deletion.author == comment_after_deletion.author
    assert comment_before_deletion.news == comment_after_deletion.news


def test_author_can_edit_comment(author_client, news, comment,
                                 detail_url_news, detail_edit_news):
    news_url = detail_url_news
    comment_url = detail_edit_news
    old_comment_text = comment.text
    edited_comment_data = NEW_TEXT_COMMENT
    response = author_client.post(comment_url, data=edited_comment_data)
    assertRedirects(response, news_url + '#comments')
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text != old_comment_text
    assert updated_comment.text == edited_comment_data['text']


def test_user_cant_edit_comment_of_another_user(admin_client, comment,
                                                detail_edit_news):
    comment_url = detail_edit_news
    edited_comment_data = {'text': 'Новый текст комментария'}
    old_comment = Comment.objects.get(pk=comment.pk)
    response = admin_client.post(comment_url, data=edited_comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_comment.text
    assert comment.author == old_comment.author
    assert comment.news == old_comment.news
