from supabase import create_client


class BotDBQuery():
    def __init__(self, url, key):
        self.url = url
        self.key = key

    def get_data(self):
        supabase = self._connect()
        record = supabase.table('tweeted_data').select('*').eq('id', 1).execute()
        data = record.data[0]['tweeted_data_json']
        return data

    def update_data(self, updated_at, data):
        supabase = self._connect()
        record = supabase.table('tweeted_data').update(
            {'updated_at': str(updated_at), 'tweeted_data_json': data}).eq('id', 1).execute()
        return record

    def _connect(self):
        return create_client(self.url, self.key)
