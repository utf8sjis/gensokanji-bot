import backoff
import tweepy
from loguru import logger

from config import Settings
from constants import MAX_RETRIES, TWEET_IMAGES_DIR
from models.tweet import TweetItem

retry_on_api_error = backoff.on_exception(
    backoff.expo, tweepy.TweepyException, max_tries=MAX_RETRIES
)


class TwitterAPI:
    """A class to interact with the Twitter API for posting tweets."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the TwitterAPI class.
        Args:
            settings (Settings): Settings object containing Twitter API credentials.
        """
        self.api_key = settings.twitter_api_key
        self.api_key_secret = settings.twitter_api_key_secret
        self.access_token = settings.twitter_access_token
        self.access_token_secret = settings.twitter_access_token_secret

        self.api = self._get_api()
        self.client = self._get_client()

    def _get_api(self) -> tweepy.API:
        """Get Twitter API v1.1 interface.
        Returns:
            tweepy.API: Twitter API v1.1 interface.
        """
        auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        return tweepy.API(auth, wait_on_rate_limit=True)

    def _get_client(self) -> tweepy.Client:
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

    @retry_on_api_error
    def post_tweet(self, tweet: TweetItem) -> bool:
        """Post the tweet.
        Args:
            tweet (TweetItem): Tweet object containing tweet data.
        Returns:
            bool: True if the tweet was posted successfully, False otherwise.
        """
        try:
            if tweet.image_paths:
                media_ids = [
                    self.api.media_upload(TWEET_IMAGES_DIR / image_path).media_id_string
                    for image_path in tweet.image_paths
                ]
            else:
                media_ids = None

            self.client.create_tweet(text=tweet.text, media_ids=media_ids)
            return True

        except tweepy.HTTPException as e:
            logger.error(f"Error: {e}")
            return False
