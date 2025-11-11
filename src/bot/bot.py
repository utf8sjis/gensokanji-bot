import random

from loguru import logger

from api_clients.database_api import DatabaseAPI
from api_clients.twitter_api import TwitterAPI
from config import get_settings


class Bot:
    """Twitter bot class to post tweets."""

    def __init__(self) -> None:
        settings = get_settings()
        self.twitter = TwitterAPI(settings)
        self.db = DatabaseAPI(settings)

    def post_regular_tweet(self) -> None:
        """Post a regular tweet."""
        candidate_ids = self.db.get_unposted_tweet_ids()
        if not candidate_ids:
            # If all tweets have been posted, reset the posted flag for all tweets.
            logger.info("🔄 Tweets have come full circle")
            self.db.reset_posted_flag()
            candidate_ids = self.db.get_unposted_tweet_ids()

        candidate_id = random.choice(candidate_ids)
        tweet = self.db.get_tweet(candidate_id)
        if not tweet:
            logger.error(f"🚨 Tweet with ID {candidate_id} not found in the database")
            return

        self.twitter.post_tweet(tweet)
        logger.info(f"✅ Success to post tweet {tweet.id}")

        self.db.flag_tweet_as_posted(tweet.id)
