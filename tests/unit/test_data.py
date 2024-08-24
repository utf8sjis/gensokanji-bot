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
    def test_tweet_validation(tweets: list[TweetDataItem]):
        for tweet in tweets:
            parsed_result = parse_tweet(tweet.text)
            if not parsed_result.valid:
                raise ValueError(f"Tweet {tweet.id} is invalid.")
