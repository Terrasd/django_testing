import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from .conftest import NEW_TEXT_COMMENT
from news.forms import WARNING
from news.models import Comment

BAD_WORDS = ('редиска', 'негодяй',)


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    url = reverse('news:detail', args=(news.id,))
    Comment.objects.all().delete()
    client.post(url, data=NEW_TEXT_COMMENT)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, news):
    url = reverse('news:detail', args=(news.id,))
    Comment.objects.all().delete()
    author_client.post(url, data=NEW_TEXT_COMMENT)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == NEW_TEXT_COMMENT['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, news, comment):
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = reverse('news:delete', args=(comment.id,))

    comments_count_before_deletion = Comment.objects.count()
    response = author_client.delete(url_to_comments)
    assertRedirects(response, news_url + '#comments')

    comments_count_after_deletion = Comment.objects.count()
    assert comments_count_after_deletion == comments_count_before_deletion - 1

    remaining_comments = Comment.objects.all()
    for remaining_comment in remaining_comments:
        assert remaining_comment != comment


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    comment_url = reverse('news:delete', args=(comment.id,))

    comments_count_before_deletion = Comment.objects.count()
    response = admin_client.delete(comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comments_count_after_deletion = Comment.objects.count()
    assert comments_count_after_deletion == comments_count_before_deletion


def test_author_can_edit_comment(author_client, news, comment):
    news_url = reverse('news:detail', args=(news.id,))
    comment_url = reverse('news:edit', args=(comment.id,))
    old_comment_text = comment.text
    edited_comment_data = NEW_TEXT_COMMENT
    response = author_client.post(comment_url, data=edited_comment_data)
    assertRedirects(response, news_url + '#comments')
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text != old_comment_text
    assert updated_comment.text == edited_comment_data['text']


def test_user_cant_edit_comment_of_another_user(admin_client, comment):
    comment_url = reverse('news:edit', args=(comment.id,))
    old_comment_text = comment.text
    edited_comment_data = NEW_TEXT_COMMENT
    response = admin_client.post(comment_url, data=edited_comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_comment_text
