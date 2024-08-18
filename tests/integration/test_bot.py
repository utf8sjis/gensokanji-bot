from unittest.mock import call, patch

import pytest

from api.database import BotDatabase
from api.twitter import TwitterAPI
from bot import Bot
from data_models import PostedData, TweetDataItem

_RANDOM_CHOICE_INDEX = -1
_TWEET_DATA_LIST = [
    TweetDataItem(id="test001", text="テスト1", images=["test1.png"]),
    TweetDataItem(id="test002", text="テスト2", images=["test2.png"]),
    TweetDataItem(id="test003", text="テスト3", images=["test3.png"]),
]


@pytest.fixture(autouse=True)
def random_choice():
    with patch("random.choice", lambda x: x[_RANDOM_CHOICE_INDEX] if x else None) as mock:
        yield mock


@pytest.fixture()
def bot_instance(mocker):
    read_tweets = mocker.patch("bot.Bot._read_tweets")
    read_tweets.return_value = _TWEET_DATA_LIST
    return Bot("")


@pytest.fixture()
def post_tweet():
    with patch.object(TwitterAPI, "post_tweet", return_value=(True, -1)) as mock:
        yield mock


@pytest.fixture()
def get_posted_data():
    with patch.object(BotDatabase, "get_posted_data") as mock:
        yield mock


@pytest.fixture()
def update_posted_data():
    with patch.object(BotDatabase, "update_posted_data") as mock:
        yield mock


class TestBot:
    @staticmethod
    def test_post_regular_tweet(bot_instance, post_tweet, get_posted_data, update_posted_data):
        # Given:
        get_posted_data.return_value = PostedData(total=1, ids=["test003"])

        # When:
        bot_instance.post_regular_tweet()

        # Then:
        post_tweet.assert_called_once_with(TweetDataItem(id="test002", text="テスト2", images=["test2.png"]))
        update_posted_data.assert_called_once_with(PostedData(total=2, ids=["test003", "test002"]))

    @staticmethod
    def test_new_cycle_tweet(bot_instance, post_tweet, get_posted_data, update_posted_data):
        # Given:
        get_posted_data.side_effect = [
            PostedData(total=len(_TWEET_DATA_LIST), ids=[tweet_data.id for tweet_data in _TWEET_DATA_LIST]),
            PostedData(total=0, ids=[]),  # If there are no candidates, initialize data on tweets already posted
        ]

        # When:
        bot_instance.post_regular_tweet()

        # Then:
        post_tweet.assert_called_once_with(TweetDataItem(id="test003", text="テスト3", images=["test3.png"]))
        update_posted_data.assert_has_calls(
            [call(PostedData(total=0, ids=[])), call(PostedData(total=1, ids=["test003"]))], any_order=False
        )
