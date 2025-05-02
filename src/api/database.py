from datetime import datetime
from zoneinfo import ZoneInfo

import supabase

from config import Settings
from data_models import PostedData
from models.tweet import TweetItem


class BotDatabase:
    def __init__(self, settings: Settings) -> None:
        """Operate the bot's database.

        Args:
            settings (Settings): Settings object containing supabase credentials.

        """
        self.api_url = settings.database_url
        self.api_key = settings.database_key
        self.tweets_table = "tweets"

    def get_posted_data(self) -> PostedData:
        """Get posted data from the database.

        Returns:
            PostedData: Data on tweets already posted

        """
        supabase = self._connect()
        records = supabase.table("bot_data").select("*").eq("id", 1).execute()
        return PostedData(**records.data[0]["posted_data"])

    def update_posted_data(self, posted_data: PostedData) -> None:
        """Update posted data in the database.

        Args:
            posted_data PostedData: Data on tweets already posted

        """
        data = {
            "updated_at": str(datetime.now(ZoneInfo("Asia/Tokyo"))),
            "posted_data": posted_data.model_dump(),
        }
        supabase = self._connect()
        supabase.table("bot_data").update(data).eq("id", 1).execute()

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

    def _connect(self) -> supabase.Client:
        """Connect to the database."""
        return supabase.create_client(self.api_url, self.api_key)
