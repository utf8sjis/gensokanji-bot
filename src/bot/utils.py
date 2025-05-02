import yaml

from constants import TWEETS_PATH
from models.tweet import TweetItem


def get_all_tweets_from_file() -> list[TweetItem]:
    with open(TWEETS_PATH) as f:
        tweets = yaml.safe_load(f)
    return [TweetItem(**tweet) for tweet in tweets]
