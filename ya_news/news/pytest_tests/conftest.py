from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.urls import reverse
import pytest

from news.models import News, Comment

TEXT_COMMENT = 'Текст комментария'
NEW_TEXT_COMMENT = {'text': 'Новый текст'}


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    new_client = client
    new_client.force_login(author)
    return client


@pytest.fixture
def guest_client(client):
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
        date=datetime.today(),
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        text=TEXT_COMMENT,
        news=news,
        author=author
    )
    return comment


@pytest.fixture
def list_news():
    today = datetime.today()
    news_list = [
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=today - timedelta(days=index)
        ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    ]
    News.objects.bulk_create(news_list)
    return news_list


@pytest.fixture
def list_comments(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            text=f'Текст {index}',
            news=news,
            author=author,
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def all_urls():
    return {
        'home': reverse('news:home'),
        'login': reverse('users:login'),
        'logout': reverse('users:logout'),
        'signup': reverse('users:signup')
    }


@pytest.fixture
def detail_url_news(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def detail_url_comm(comment):
    return reverse('news:detail', args=(comment.id,))


@pytest.fixture
def detail_del_news(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def detail_edit_news(news):
    return reverse('news:edit', args=(news.id,))


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
@pytest.fixture
def url_name_args(name, comment):
    return reverse(name, args=(comment.id,))
