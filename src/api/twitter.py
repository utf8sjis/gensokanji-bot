from pathlib import Path

import tweepy
from loguru import logger

from config import Settings
from data_models import TweetDataItem


class TwitterAPI:
    def __init__(
        self,
        tweets_data_dir: Path,
        settings: Settings,
    ) -> None:
        """Operate using Twitter API.

        Args:
            tweets_data_dir (Path): Path to the directory of tweets data.
            settings (Settings): Settings object containing Twitter API credentials.

        """
        self.tweets_data_dir = tweets_data_dir
        self.api_key = settings.twitter_api_key
        self.api_key_secret = settings.twitter_api_key_secret
        self.access_token = settings.twitter_access_token
        self.access_token_secret = settings.twitter_access_token_secret

    def post_tweet(self, tweet: TweetDataItem) -> bool:
        """Post the tweet.

        Args:
            tweet (TweetDataItem): Text and image data of the tweet.

        Returns:
            bool: True if successful, false otherwise.

        """
        twitter_api = self._api()
        client = self._client()

        try:
            media_ids = None
            if tweet.images:
                media_ids = [
                    twitter_api.media_upload(self.tweets_data_dir / "images" / file_name).media_id_string
                    for file_name in tweet.images
                ]
            client.create_tweet(text=tweet.text, media_ids=media_ids)
            logger.info(f"Success to post tweet {tweet.id}")
            return True

        except tweepy.HTTPException as e:
            logger.error(f"Failed to post tweet {tweet.id}")
            logger.error(f"Error: {e}")
            return False

    def _api(self) -> tweepy.API:
        """Get Twitter API v1.1 interface.

        Returns:
            API: Twitter API v1.1 interface.

        """
        auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        return tweepy.API(auth, wait_on_rate_limit=True)

    def _client(self) -> tweepy.Client:
        """Get Twitter API v2 client.

        Returns:
            Client: Twitter API v2 client.

        """
        return tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_key_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
        )
