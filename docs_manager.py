import os

import bs4
import openai

import database
import utilities

def preprocess(url, mgr):
    old_page_text = mgr.get_page_text(url)
    soup = bs4.BeautifulSoup(old_page_text, 'html.parser')
    main = soup.select('div.main')[0]
    for tag in ['script', 'style', 'link']:
        for useless_node in main.find_all(tag):
            useless_node.decompose()
    new_page_text = str(main)
    mgr.set_page_text(url, new_page_text)

def segment(page_url, mgr):
    page_text = mgr.get_page_text(page_url)
    soup = bs4.BeautifulSoup(page_text, 'html.parser')
    for section in soup.find_all('section'):
        segment = str(section)
        section_id = section.get('id')
        if not section_id:
            continue
        segment_url = f'{page_url}#{section_id}'
        mgr.set_segment(segment_url, segment)

def embed(url, text, checksums):
    openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_KEY'))
    max_token_count = 8191
    model = 'text-embedding-ada-002'
    db = database.Database()
    if utilities.token_count(text) > max_token_count:
        return
    if db.row_exists(content=text, checksums=checksums):
        db.update_timestamp(content=text)
    else:
        embedding = openai_client.embeddings.create(
            input=text,
            model='text-embedding-ada-002'
        ).data[0].embedding
        db.add(content=text, content_type='web', url=url, embedding=embedding)
