import os
import time

import dotenv
import supabase

import utilities

class Database:
    def __init__(self):
        dotenv.load_dotenv()
        self._db = supabase.create_client(
            supabase_url=os.environ.get('SUPABASE_URL'),
            supabase_key=os.environ.get('SUPABASE_KEY')
        )
        self._table = self._db.table('embeddings')

    def update_timestamp(self, content=None):
        self._table.update({
            'timestamp': utilities.timestamp()
        }).eq(
            'checksum',
            utilities.checksum(content)
        ).execute()

    def row_exists(self, content=None):
        try:
            checksum = utilities.checksum(content)
            rows = self._table.select('*').eq('checksum', checksum).execute()
            return True if len(rows.data) > 0 else False
        except Exception as e:
            return False

    def add(self, content=None, url=None, content_type=None, embedding=None):
        try:
            self._table.insert({
                'checksum': utilities.checksum(content),
                'type': content_type,
                'token_count': utilities.token_count(content),
                'content': content,
                'url': url,
                'timestamp': utilities.timestamp(),
                'embedding': embedding
            }).execute()
        except Exception as e:
            return None

    def prune(self):
        one_day_in_seconds = 60 * 60 * 24
        current_time = int(time.time())
        max_age = current_time - one_day_in_seconds
        self._table.delete().lt('timestamp', max_age).execute()
