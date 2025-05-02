import tweepy
from loguru import logger

from config import Settings
from constants import TWEET_IMAGES_DIR
from models.tweet import TweetItem


class TwitterAPI:
    """Twitter API class to handle posting tweets."""

    def __init__(self, settings: Settings):
        """Initialize the TwitterAPI class.
        Args:
            settings (Settings): Settings object containing Twitter API credentials.
        """
        self.api_key = settings.twitter_api_key
        self.api_key_secret = settings.twitter_api_key_secret
        self.access_token = settings.twitter_access_token
        self.access_token_secret = settings.twitter_access_token_secret

    def post_tweet(self, tweet: TweetItem) -> bool:
        """Post the tweet.
        Args:
            tweet (TweetItem): Tweet object containing tweet data.
        Returns:
            bool: True if the tweet was posted successfully, False otherwise.
        """
        api = self._api()
        client = self._client()

        try:
            if tweet.image_paths:
                media_ids = [
                    api.media_upload(TWEET_IMAGES_DIR / image_path).media_id_string
                    for image_path in tweet.image_paths
                ]
            else:
                media_ids = None

            client.create_tweet(text=tweet.text, media_ids=media_ids)
            return True

        except tweepy.HTTPException as e:
            logger.error(f"Error: {e}")
            return False

    def _api(self) -> tweepy.API:
        """Get Twitter API v1.1 interface.
        Returns:
            tweepy.API: Twitter API v1.1 interface.
        """
        auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        return tweepy.API(auth, wait_on_rate_limit=True)

    def _client(self) -> tweepy.Client:
        """Get Twitter API v2 client.
        Returns:
            tweepy.Client: Twitter API v2 client.
        """
        return tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_key_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
        )
