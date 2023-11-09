import bs4
import mbedmgr

import database
import utilities

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

def segment(url, data):
    soup = bs4.BeautifulSoup(data[url]['text'], 'html.parser')
    sections = []
    for section in soup.find_all('section'):
        sections.append(str(section))
    data[url]['sections'] = sections

def embed(url, data):
    db = database.Database()
    for section in data[url]['sections']:
        checksum = hashlib.md5(section.encode('utf-8')).hexdigest()
        # check if section exists in db
        # update timestamp if yes
        # create row if no
        # create embedding as part of create row process
        print(checksum)

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
