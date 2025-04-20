import pytest
import yaml
from twitter_text import parse_tweet

from constants import DATA_DIR
from data_models import TweetData, TweetDataItem


@pytest.fixture
def tweets():
    with open(DATA_DIR / "tweets.yml") as f:
        tweets_data = TweetData(**yaml.safe_load(f))

    return tweets_data.tweets


class TestData:
    @staticmethod
    def test_tweet_id_uniqueness(tweets: list[TweetDataItem]):
        tweet_ids = [tweet.id for tweet in tweets]
        assert len(tweet_ids) == len(set(tweet_ids))

    @staticmethod
    def test_tweet_validation(tweets: list[TweetDataItem]):
        for tweet in tweets:
            parsed_result = parse_tweet(tweet.text)
            if not parsed_result.valid:
                raise AssertionError(f"Tweet {tweet.id} is invalid.")

    @staticmethod
    def test_image_count(tweets: list[TweetDataItem]):
        for tweet in tweets:
            assert len(tweet.images) <= 4

    @staticmethod
    def test_image_existence(tweets: list[TweetDataItem]):
        for tweet in tweets:
            for image in tweet.images:
                assert (DATA_DIR / "images" / image).exists()
