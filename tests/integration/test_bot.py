from unittest.mock import patch

import pytest

from api.database import BotDatabase
from api.twitter import TwitterAPI
from bot.bot import Bot
from models.tweet import TweetItem

_RANDOM_CHOICE_INDEX = -1

_TWEETS = [
    TweetItem(
        id="test001",
        type="regular",
        group="test",
        text="テスト1",
        image_paths=["test1.png"],
    ),
    TweetItem(
        id="test002",
        type="regular",
        group="test",
        text="テスト2",
        image_paths=["test2.png"],
    ),
    TweetItem(
        id="test003",
        type="regular",
        group="test",
        text="テスト3",
        image_paths=["test3.png"],
    ),
]


@pytest.fixture()
def mock_get_unposted_tweet_ids():
    with patch.object(BotDatabase, "get_unposted_tweet_ids") as mock:
        yield mock


@pytest.fixture()
def mock_get_tweet():
    with patch.object(
        BotDatabase,
        "get_tweet",
        side_effect=lambda x: next(tweet for tweet in _TWEETS if tweet.id == x),
    ) as mock:
        yield mock


@pytest.fixture()
def mock_post_tweet():
    with patch.object(TwitterAPI, "post_tweet") as mock:
        yield mock


@pytest.fixture()
def mock_flag_tweet_as_posted():
    with patch.object(BotDatabase, "flag_tweet_as_posted") as mock:
        yield mock


@pytest.fixture()
def mock_reset_posted_flag():
    with patch.object(BotDatabase, "reset_posted_flag") as mock:
        yield mock


@pytest.fixture(autouse=True)
def random_choice():
    with patch("random.choice", lambda x: x[_RANDOM_CHOICE_INDEX]) as mock:
        yield mock


class TestBot:
    @staticmethod
    def test_post_regular_tweet(
        mock_get_unposted_tweet_ids,
        mock_reset_posted_flag,
        mock_get_tweet,
        mock_post_tweet,
        mock_flag_tweet_as_posted,
    ):
        # Given:
        mock_get_unposted_tweet_ids.return_value = ["test001", "test002"]
        mock_post_tweet.return_value = True

        # When:
        Bot().post_regular_tweet()

        # Then:
        mock_get_unposted_tweet_ids.assert_called_once()
        mock_reset_posted_flag.assert_not_called()
        mock_get_tweet.assert_called_once_with("test002")
        mock_post_tweet.assert_called_once_with(
            TweetItem(
                id="test002",
                type="regular",
                group="test",
                text="テスト2",
                image_paths=["test2.png"],
            )
        )
        mock_flag_tweet_as_posted.assert_called_once_with("test002")

    @staticmethod
    def test_post_regular_tweet_not_found(
        mock_get_unposted_tweet_ids,
        mock_reset_posted_flag,
        mock_get_tweet,
        mock_post_tweet,
        mock_flag_tweet_as_posted,
    ):
        # Given:
        mock_get_unposted_tweet_ids.return_value = ["test001", "test002"]
        mock_get_tweet.side_effect = None
        mock_get_tweet.return_value = None

        # When:
        Bot().post_regular_tweet()

        # Then:
        mock_get_unposted_tweet_ids.assert_called_once()
        mock_reset_posted_flag.assert_not_called()
        mock_get_tweet.assert_called_once_with("test002")
        # If the tweet is not found, do not post anything.
        mock_post_tweet.assert_not_called()
        mock_flag_tweet_as_posted.assert_not_called()

    @staticmethod
    def test_post_regular_tweet_failure(
        mock_get_unposted_tweet_ids,
        mock_reset_posted_flag,
        mock_get_tweet,
        mock_post_tweet,
        mock_flag_tweet_as_posted,
    ):
        # Given:
        mock_get_unposted_tweet_ids.return_value = ["test001", "test002"]
        mock_post_tweet.return_value = False

        # When:
        Bot().post_regular_tweet()

        # Then:
        mock_get_unposted_tweet_ids.assert_called_once()
        mock_reset_posted_flag.assert_not_called()
        mock_get_tweet.assert_called_once_with("test002")
        mock_post_tweet.assert_called_once_with(
            TweetItem(
                id="test002",
                type="regular",
                group="test",
                text="テスト2",
                image_paths=["test2.png"],
            )
        )
        # The tweet is not flagged as posted since posting failed.
        mock_flag_tweet_as_posted.assert_not_called()

    @staticmethod
    def test_post_regular_tweet_with_new_cycle(
        mock_get_unposted_tweet_ids,
        mock_reset_posted_flag,
        mock_get_tweet,
        mock_post_tweet,
        mock_flag_tweet_as_posted,
    ):
        # Given:
        # If all tweets have been posted, reset the posted flag for all tweets.
        mock_get_unposted_tweet_ids.side_effect = [
            [],
            ["test001", "test002", "test003"],
        ]
        mock_post_tweet.return_value = True

        # When:
        Bot().post_regular_tweet()

        # Then:
        assert mock_get_unposted_tweet_ids.call_count == 2
        mock_reset_posted_flag.assert_called_once()
        mock_get_tweet.assert_called_once_with("test003")
        mock_post_tweet.assert_called_once_with(
            TweetItem(
                id="test003",
                type="regular",
                group="test",
                text="テスト3",
                image_paths=["test3.png"],
            )
        )
        mock_flag_tweet_as_posted.assert_called_once_with("test003")
