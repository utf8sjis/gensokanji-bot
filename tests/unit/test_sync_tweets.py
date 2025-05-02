from unittest.mock import patch

import pytest

from api.database import BotDatabase
from bot.sync_tweets import sync_tweets
from models.tweet import TweetItem

FILE_TWEETS = [
    TweetItem(
        id="main002",
        type="regular",
        group="main",
        text="テスト2",
        image_paths=["main002.png"],
    ),
    TweetItem(
        id="main003",
        type="regular",
        group="main",
        text="テスト3-1",
        image_paths=["main003.png"],
    ),
    TweetItem(
        id="main004",
        type="regular",
        group="main",
        text="テスト4",
        image_paths=["main004-1.png", "main004-2.png"],
    ),
    TweetItem(
        id="main005",
        type="regular",
        group="main",
        text="テスト5",
        image_paths=["main005.png"],
    ),
]

DB_TWEETS = [
    TweetItem(
        id="main001",
        type="regular",
        group="main",
        text="テスト1",
        image_paths=["main001.png"],
    ),
    TweetItem(
        id="main002",
        type="regular",
        group="main",
        text="テスト2",
        image_paths=["main002.png"],
    ),
    TweetItem(
        id="main003",
        type="regular",
        group="main",
        text="テスト3",
        image_paths=["main003.png"],
    ),
    TweetItem(
        id="main004",
        type="regular",
        group="main",
        text="テスト4",
        image_paths=["main004.png"],
    ),
]


@pytest.fixture(autouse=True)
def mock_get_all_tweets_from_file():
    with patch(
        "bot.sync_tweets.get_all_tweets_from_file", return_value=FILE_TWEETS
    ) as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_get_all_tweets():
    with patch.object(BotDatabase, "get_all_tweets", return_value=DB_TWEETS) as mock:
        yield mock


@pytest.fixture()
def mock_delete_tweets():
    with patch.object(BotDatabase, "delete_tweets") as mock:
        yield mock


@pytest.fixture()
def mock_update_tweets():
    with patch.object(BotDatabase, "update_tweets") as mock:
        yield mock


class TestSyncTweets:
    @staticmethod
    def test_sync_tweets(mock_delete_tweets, mock_update_tweets):
        # When:
        sync_tweets()

        # Then:
        mock_delete_tweets.assert_called_once_with(["main001"])
        # Called with new tweets ([main005]) + updated tweets ([main003, main004])
        mock_update_tweets.assert_called_once_with(
            [
                TweetItem(
                    id="main005",
                    type="regular",
                    group="main",
                    text="テスト5",
                    image_paths=["main005.png"],
                ),
                TweetItem(
                    id="main003",
                    type="regular",
                    group="main",
                    text="テスト3-1",
                    image_paths=["main003.png"],
                ),
                TweetItem(
                    id="main004",
                    type="regular",
                    group="main",
                    text="テスト4",
                    image_paths=["main004-1.png", "main004-2.png"],
                ),
            ]
        )
