from unittest.mock import call, patch

import pytest

from api.database import BotDatabase
from api.twitter import TwitterAPI
from bot import Bot
from data_models import PostedData, TweetData

_RANDOM_CHOICE_INDEX = -1
_TWEET_DATA_LIST = [
    TweetData(id="test001", text="テスト1", images=["test1.png"]),
    TweetData(id="test002", text="テスト2", images=["test2.png"]),
    TweetData(id="test003", text="テスト3", images=["test3.png"]),
]


@pytest.fixture(autouse=True)
def random_choice_mock():
    with patch("random.choice", lambda x: x[_RANDOM_CHOICE_INDEX] if x else None) as mock:
        yield mock


@pytest.fixture()
def read_tweets_mock():
    with patch.object(Bot, "_read_tweets") as mock:
        yield mock


@pytest.fixture()
def get_posted_data_mock():
    with patch.object(BotDatabase, "get_posted_data") as mock:
        yield mock


@pytest.fixture()
def post_tweet_mock():
    with patch.object(TwitterAPI, "post_tweet", return_value=(True, -1)) as mock:
        yield mock


@pytest.fixture()
def update_posted_data_mock():
    with patch.object(BotDatabase, "update_posted_data") as mock:
        yield mock


class TestBot:
    @staticmethod
    def test_post_regular_tweet(read_tweets_mock, get_posted_data_mock, post_tweet_mock, update_posted_data_mock):
        # Given:
        read_tweets_mock.return_value = _TWEET_DATA_LIST
        get_posted_data_mock.return_value = PostedData(total=1, ids=["test003"])

        # When:
        bot = Bot("")
        bot.post_regular_tweet()

        # Then:
        post_tweet_mock.assert_called_once_with(TweetData(id="test002", text="テスト2", images=["test2.png"]))
        update_posted_data_mock.assert_called_once_with(PostedData(total=2, ids=["test003", "test002"]))

    @staticmethod
    def test_new_cycle_tweet(read_tweets_mock, get_posted_data_mock, post_tweet_mock, update_posted_data_mock):
        # Given:
        read_tweets_mock.return_value = _TWEET_DATA_LIST
        get_posted_data_mock.side_effect = [
            PostedData(total=len(_TWEET_DATA_LIST), ids=[tweet_data.id for tweet_data in _TWEET_DATA_LIST]),
            PostedData(total=0, ids=[]),  # If there are no candidates, initialize data on tweets already posted
        ]

        # When:
        bot = Bot("")
        bot.post_regular_tweet()

        # Then:
        post_tweet_mock.assert_called_once_with(TweetData(id="test003", text="テスト3", images=["test3.png"]))
        update_posted_data_mock.assert_has_calls(
            [call(PostedData(total=0, ids=[])), call(PostedData(total=1, ids=["test003"]))]
        )