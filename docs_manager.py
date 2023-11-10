import os

import bs4
import openai

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
    openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_KEY'))
    max_token_count = 8191
    model = 'text-embedding-ada-002'
    db = database.Database()
    for section in data[url]['sections']:
        if utilities.token_count(section) > max_token_count:
            continue
        if db.row_exists(content=section):
            db.update_timestamp(content=section)
        else:
            embedding = openai_client.embeddings.create(
                input=section,
                model='text-embedding-ada-002'
            ).data[0].embedding
            db.add(content=section, content_type='web', url=url, embedding=embedding)