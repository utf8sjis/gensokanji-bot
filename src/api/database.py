from datetime import datetime
from zoneinfo import ZoneInfo

import supabase

from config import Settings
from models.tweet import TweetItem


class BotDatabase:
    """Database class to handle tweet data."""

    def __init__(self, settings: Settings):
        """Initialize the BotDatabase class.
        Args:
            settings (Settings): Settings object containing supabase credentials.
        """
        self.api_url = settings.database_url
        self.api_key = settings.database_key
        self.tweets_table = "tweets"

    def get_all_tweets(self) -> list[TweetItem]:
        """Get all tweets from the database.
        Returns:
            list[TweetItem]: List of all tweets in the database.
        """
        supabase = self._connect()
        records = (
            supabase.table(self.tweets_table)
            .select("id", "type", "group", "text", "image_paths")
            .execute()
        )

        return [TweetItem(**record) for record in records.data]

    def get_tweet(self, tweet_id: str) -> TweetItem | None:
        """Get a specific tweet from the database.
        Args:
            tweet_id (str): ID of the tweet to be retrieved.
        Returns:
            TweetItem | None: The tweet object if found, None otherwise.
        """
        supabase = self._connect()
        record = (
            supabase.table(self.tweets_table)
            .select("id", "type", "group", "text", "image_paths")
            .eq("id", tweet_id)
            .execute()
        )

        if record.data:
            return TweetItem(**record.data[0])

        return None

    def get_unposted_tweet_ids(self) -> list[str]:
        """Get IDs of tweets that have not been posted yet.
        Returns:
            list[str]: List of IDs of unposted tweets.
        """
        supabase = self._connect()
        records = (
            supabase.table(self.tweets_table)
            .select("id")
            .eq("type", "regular")
            .eq("is_posted", False)
            .execute()
        )

        return [record["id"] for record in records.data]

    def delete_tweets(self, ids: list[str]):
        """Delete tweets from the database.
        Args:
            ids (list[str]): IDs of tweets to be deleted.
        """
        supabase = self._connect()
        supabase.table(self.tweets_table).delete().in_("id", ids).execute()

    def update_tweets(self, tweets: list[TweetItem]):
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

        supabase = self._connect()
        supabase.table(self.tweets_table).upsert(data).execute()

    def flag_tweet_as_posted(self, tweet_id: str):
        """Flag a tweet as posted in the database.
        Args:
            tweet_id (str): ID of the tweet to be flagged as posted.
        """
        supabase = self._connect()
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        supabase.table(self.tweets_table).update(
            {"is_posted": True, "posted_at": now}
        ).eq("id", tweet_id).execute()

    def reset_posted_flag(self):
        """Reset the posted flag for all tweets in the database."""
        supabase = self._connect()
        supabase.table(self.tweets_table).update({"is_posted": False}).eq(
            "type", "regular"
        ).execute()

    def _connect(self) -> supabase.Client:
        """Connect to the database."""
        return supabase.create_client(self.api_url, self.api_key)
