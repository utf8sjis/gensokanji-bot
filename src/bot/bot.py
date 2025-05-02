import random

from loguru import logger

from api.database import BotDatabase
from api.twitter import TwitterAPI
from config import get_settings


class Bot:
    """Twitter bot class to post tweets."""

    def __init__(self):
        settings = get_settings()
        self.twitter_api = TwitterAPI(settings)
        self.bot_db = BotDatabase(settings)

    def post_regular_tweet(self):
        """Post a regular tweet."""
        candidate_ids = self.bot_db.get_unposted_tweet_ids()
        if not candidate_ids:
            # If all tweets have been posted, reset the posted flag for all tweets.
            logger.info("🔄 Tweets have come full circle")
            self.bot_db.reset_posted_flag()
            candidate_ids = self.bot_db.get_unposted_tweet_ids()

        candidate_id = random.choice(candidate_ids)
        tweet = self.bot_db.get_tweet(candidate_id)
        if not tweet:
            logger.error(f"🚨 Tweet with ID {candidate_id} not found in the database")
            return

        if self.twitter_api.post_tweet(tweet):
            logger.info(f"✅ Success to post tweet {tweet.id}")
            self.bot_db.flag_tweet_as_posted(tweet.id)
        else:
            logger.error(f"🚨 Failed to post tweet {tweet.id}")
