from datetime import datetime
from zoneinfo import ZoneInfo

import supabase

from config import Settings
from models.tweet import TweetItem


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

    def delete_tweets(self, ids: list[str]) -> None:
        """Delete tweets from the database.
        Args:
            ids (list[str]): IDs of tweets to be deleted.
        """
        self.client.table(self.tweets_table).delete().in_("id", ids).execute()

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

    def flag_tweet_as_posted(self, tweet_id: str) -> None:
        """Flag a tweet as posted in the database.
        Args:
            tweet_id (str): ID of the tweet to be flagged as posted.
        """
        self.client.table(self.tweets_table).update(
            {"is_posted": True, "posted_at": datetime.now(ZoneInfo("Asia/Tokyo"))}
        ).eq("id", tweet_id).execute()

    def reset_posted_flag(self) -> None:
        """Reset the posted flag for all tweets in the database."""
        self.client.table(self.tweets_table).update({"is_posted": False}).eq(
            "type", "regular"
        ).execute()
