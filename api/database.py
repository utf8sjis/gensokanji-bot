from supabase import create_client


class BotDatabase():
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    def get_posted_data(self):
        supabase = self._connect()
        record = supabase.table('tweeted_data').select('*').eq('id', 1).execute()
        posted_data = record.data[0]
        return posted_data

    def update_posted_data(self, posted_data):
        supabase = self._connect()
        record = supabase.table('tweeted_data').update(posted_data).eq('id', 1).execute()
        return record

    def _connect(self):
        return create_client(self.api_url, self.api_key)
