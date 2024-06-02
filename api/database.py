import supabase
from data_models import PostedData
from utils import get_current_datetime


class BotDatabase:
    def __init__(self, api_url: str, api_key: str) -> None:
        """Operate the bot's database.

        Args:
            api_url (str): URL for the supabase project.
            api_key (str): API key for the supabase project.

        """
        self.api_url = api_url
        self.api_key = api_key

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
            "updated_at": str(get_current_datetime()),
            "posted_data": posted_data.model_dump(),
        }
        supabase = self._connect()
        supabase.table("bot_data").update(data).eq("id", 1).execute()

    def _connect(self) -> supabase.Client:
        """Connect to the database."""
        return supabase.create_client(self.api_url, self.api_key)
