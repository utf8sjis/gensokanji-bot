import pytest
from twitter_text import parse_tweet

from bot.utils import get_all_tweets_from_file
from constants import DATA_DIR
from models.tweet import TweetItem


@pytest.fixture
def tweets() -> list[TweetItem]:
    return get_all_tweets_from_file()


class TestData:
    @staticmethod
    def test_tweet_id_uniqueness(tweets):
        tweet_ids = [tweet.id for tweet in tweets]
        assert len(tweet_ids) == len(set(tweet_ids))

    @staticmethod
    def test_tweet_validation(tweets):
        for tweet in tweets:
            parsed_result = parse_tweet(tweet.text)
            if not parsed_result.valid:
                raise AssertionError(f"Tweet {tweet.id} is invalid.")

    @staticmethod
    def test_image_count(tweets):
        for tweet in tweets:
            assert len(tweet.image_paths) <= 4

    @staticmethod
    def test_image_existence(tweets):
        for tweet in tweets:
            for image_path in tweet.image_paths:
                assert (DATA_DIR / "images" / image_path).exists()
