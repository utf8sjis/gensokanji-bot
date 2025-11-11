from datetime import datetime
from zoneinfo import ZoneInfo

import backoff
import httpx
import supabase
from postgrest.exceptions import APIError

from config import Settings
from constants import MAX_RETRIES
from models.tweet import TweetItem

retry_on_api_error = backoff.on_exception(
    backoff.expo, (APIError, httpx.HTTPError), max_tries=MAX_RETRIES
)


class DatabaseAPI:
    """A class to interact with the database using Supabase."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the DatabaseAPI class.
        Args:
            settings (Settings): Settings object containing Supabase credentials.
        """
        self.database_url = settings.database_url
        self.database_key = settings.database_key
        self.tweets_table = "tweets"

        self.client = self._get_client()

    def _get_client(self) -> supabase.Client:
        """Get Supabase client.
        Returns:
            supabase.Client: Supabase client.
        """
        return supabase.create_client(self.database_url, self.database_key)

    @retry_on_api_error
    def get_all_tweets(self) -> list[TweetItem]:
        """Get all tweets from the database.
        Returns:
            list[TweetItem]: List of all tweets in the database.
        """
        records = (
            self.client.table(self.tweets_table)
            .select("id", "type", "group", "text", "image_paths")
            .execute()
        )

        return [TweetItem(**record) for record in records.data]

    @retry_on_api_error
    def get_tweet(self, tweet_id: str) -> TweetItem | None:
        """Get a specific tweet from the database.
        Args:
            tweet_id (str): ID of the tweet to be retrieved.
        Returns:
            TweetItem | None: The tweet object if found, None otherwise.
        """
        record = (
            self.client.table(self.tweets_table)
            .select("id", "type", "group", "text", "image_paths")
            .eq("id", tweet_id)
            .execute()
        )

        if record.data:
            return TweetItem(**record.data[0])

        return None

    @retry_on_api_error
    def get_unposted_tweet_ids(self) -> list[str]:
        """Get IDs of tweets that have not been posted yet.
        Returns:
            list[str]: List of IDs of unposted tweets.
        """
        records = (
            self.client.table(self.tweets_table)
            .select("id")
            .eq("type", "regular")
            .eq("is_posted", False)
            .execute()
        )

        return [record["id"] for record in records.data]

    @retry_on_api_error
    def delete_tweets(self, ids: list[str]) -> None:
        """Delete tweets from the database.
        Args:
            ids (list[str]): IDs of tweets to be deleted.
        """
        self.client.table(self.tweets_table).delete().in_("id", ids).execute()

    @retry_on_api_error
    def update_tweets(self, tweets: list[TweetItem]) -> None:
        """Update tweets in the database.
        Args:
            tweets (list[TweetItem]): List of tweets to be updated, including new.
        """
        data = []
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        for tweet in tweets:
            data.append(
                {
                    "updated_at": str(now),
                    "content_updated_at": str(now),
                    **tweet.model_dump(),
                }
            )

        self.client.table(self.tweets_table).upsert(data).execute()

    @retry_on_api_error
    def flag_tweet_as_posted(self, tweet_id: str) -> None:
        """Flag a tweet as posted in the database.
        Args:
            tweet_id (str): ID of the tweet to be flagged as posted.
        """
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        self.client.table(self.tweets_table).update(
            {"updated_at": str(now), "is_posted": True, "posted_at": str(now)}
        ).eq("id", tweet_id).execute()

    @retry_on_api_error
    def reset_posted_flag(self) -> None:
        """Reset the posted flag for all tweets in the database."""
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        self.client.table(self.tweets_table).update(
            {"updated_at": str(now), "is_posted": False}
        ).eq("type", "regular").execute()
