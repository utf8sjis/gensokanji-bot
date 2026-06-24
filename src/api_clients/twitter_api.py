import json
from urllib.request import Request, urlopen

import backoff
import tweepy

from config import Settings
from constants import MAX_RETRIES, TWEET_IMAGES_DIR
from models.tweet import TweetItem

_MEDIA_URL_PREFIXES = ("http://", "https://")
_NO_RETRY_EXCEPTIONS = (
    tweepy.BadRequest,
    tweepy.Unauthorized,
    tweepy.Forbidden,
    tweepy.NotFound,
)
_TWITTER_BACKEND = "twitter"
_XQUIK_BACKEND = "xquik"
_SUPPORTED_BACKENDS = {_TWITTER_BACKEND, _XQUIK_BACKEND}
_XQUIK_TIMEOUT_SECONDS = 30

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
        self.post_backend = settings.x_post_backend.strip().lower()
        if self.post_backend not in _SUPPORTED_BACKENDS:
            raise ValueError(
                f"Unsupported post backend: {settings.x_post_backend}. "
                f"Expected one of {sorted(_SUPPORTED_BACKENDS)}."
            )

        self.api_key = settings.twitter_api_key
        self.api_key_secret = settings.twitter_api_key_secret
        self.access_token = settings.twitter_access_token
        self.access_token_secret = settings.twitter_access_token_secret
        self.xquik_api_key = settings.xquik_api_key
        self.xquik_account = settings.xquik_account
        self.xquik_create_tweet_url = settings.xquik_create_tweet_url

        self.api: tweepy.API | None = None
        self.client: tweepy.Client | None = None

        if self.post_backend == _XQUIK_BACKEND:
            return

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

    def post_tweet(self, tweet: TweetItem) -> None:
        """Post the tweet.
        Args:
            tweet (TweetItem): Tweet object containing tweet data.
        """
        if self.post_backend == _XQUIK_BACKEND:
            self._post_tweet_with_xquik(tweet)
            return

        self._post_tweet_with_twitter(tweet)

    @retry_on_api_error
    def _post_tweet_with_twitter(self, tweet: TweetItem) -> None:
        if self.api is None or self.client is None:
            raise RuntimeError("Twitter client is not initialized.")

        try:
            if tweet.image_paths:
                media_ids = [
                    self.api.media_upload(TWEET_IMAGES_DIR / image_path).media_id_string
                    for image_path in tweet.image_paths
                ]
            else:
                media_ids = None

            self.client.create_tweet(text=tweet.text, media_ids=media_ids)

        except _NO_RETRY_EXCEPTIONS:
            raise

    def _post_tweet_with_xquik(self, tweet: TweetItem) -> None:
        if not self.xquik_api_key:
            raise ValueError("XQUIK_API_KEY is required for the xquik backend.")
        if not self.xquik_account:
            raise ValueError("XQUIK_ACCOUNT is required for the xquik backend.")

        body: dict[str, str | list[str]] = {
            "account": self.xquik_account,
            "text": tweet.text,
        }
        media_urls = self._get_xquik_media_urls(tweet)
        if media_urls:
            body["media"] = media_urls

        request = Request(
            self.xquik_create_tweet_url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self.xquik_api_key,
            },
            method="POST",
        )
        with urlopen(request, timeout=_XQUIK_TIMEOUT_SECONDS) as response:
            response.read()

    @staticmethod
    def _get_xquik_media_urls(tweet: TweetItem) -> list[str]:
        media_urls: list[str] = []
        for image_path in tweet.image_paths:
            if not image_path.startswith(_MEDIA_URL_PREFIXES):
                raise ValueError(
                    "Xquik media must be public URLs. "
                    "Use the twitter backend for local image files."
                )
            media_urls.append(image_path)
        return media_urls
