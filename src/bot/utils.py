import yaml

from constants import DATA_DIR
from models.tweet import TweetItem


def get_all_tweets_from_file() -> list[TweetItem]:
    with open(DATA_DIR / "tweets.yml") as f:
        tweets = yaml.safe_load(f)
    return [TweetItem(**tweet) for tweet in tweets]
