from supabase import create_client


class BotDatabase():
    def __init__(self, api_url, api_key):
        """Operate the bot's database.

        Args:
            api_url (str): URL for the supabase project.
            api_key (str): API key for the supabase project.

        """
        self.api_url = api_url
        self.api_key = api_key

    def get_posted_data(self):
        """Get data from the database.

        Returns:
            dict: Data such as last updated date and time, tweets
                already posted, etc.

        """
        supabase = self._connect()
        record = supabase.table('tweeted_data').select('*').eq('id', 1).execute()
        posted_data = record.data[0]
        return posted_data

    def update_posted_data(self, posted_data):
        """Update data in the database.

        Args:
            posted_data (dict): Data such as last updated date and time,
                tweets already posted, etc.

        """
        supabase = self._connect()
        supabase.table('tweeted_data').update(posted_data).eq('id', 1).execute()

    def _connect(self):
        """Connect to the database.

        """
        return create_client(self.api_url, self.api_key)
