import typing
import hashlib
import json
import time
import os

import bs4
import tiktoken
import mbedmgr
import dotenv
import supabase

def preprocess(url, data):
    soup = bs4.BeautifulSoup(data[url]['text'], 'html.parser')
    main = soup.select('div.main')[0]
    for script in main.find_all('script'):
        script.decompose()
    for style in main.find_all('style'):
        style.decompose()
    for link in main.find_all('link'):
        link.decompose()
    data[url]['text'] = str(main)

# TODO: Rename the data arg or figure out some way to prevent against
# accidentally overwriting the data coming from mbedmgr...
def segment(url, data):
    table_name = 'embeddings'
    soup = bs4.BeautifulSoup(data[url]['text'], 'html.parser')
    sections = []
    for section in soup.find_all('section'):
        section = str(section)
        checksum = hashlib.md5(section.encode('utf-8')).hexdigest()
        token_count = len(token_encoder.encode(section))
        # Skip the section if it's too big to convert into an embedding.
        if token_count > max_token_count:
            continue
        sections.append(section)
        timestamp = int(time.time())
        rows = database.table(table_name).select('*').eq('checksum', checksum).execute()
        exists = True if len(rows.data) > 0 else False
        if exists:
            database.table(table_name).update({'timestamp': timestamp}).eq('checksum', checksum).execute()
        else:
            database.table(table_name).insert({
                'checksum': checksum,
                'type': 'web',
                'token_count': len(token_encoder.encode(section)),
                'content': section,
                'url': url,
                'timestamp': timestamp
            }).execute()
    data[url]['sections'] = sections

def embed(url, data):
    for section in data[url]['sections']:
        checksum = hashlib.md5(section.encode('utf-8')).hexdigest()
        print(checksum)


# Init.
dotenv.load_dotenv()
database = supabase.create_client(
    supabase_url=os.environ.get('SUPABASE_URL'),
    supabase_key=os.environ.get('SUPABASE_KEY')
)

# Main vars.
token_encoder = tiktoken.get_encoding('cl100k_base')
max_token_count = 8191
embedding_model = 'text-embedding-ada-002'
manager = mbedmgr.EmbeddingsManager()

# Generate embeddings for the official docs.
docs_site = manager.add_website_source(source_id='https://pigweed.dev')
docs_site.get_pages_from_sitemap('https://pigweed.dev/sitemap.xml')
docs_site.preprocess_handler = preprocess
docs_site.segment_handler = segment
docs_site.embed_handler = embed
manager.generate()
