import os

import bs4
import mbedmgr
import openai
import dotenv

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

dotenv.load_dotenv()

openai.api_key = os.environ.get('OPENAI_KEY')

manager = mbedmgr.EmbeddingsManager()

# docs_site = manager.add_website_source(source_id='https://pigweed.dev')
# docs_site.get_pages_from_sitemap('https://pigweed.dev/sitemap.xml')
# docs_site.preprocess_handler = preprocess
# docs_site.segment_handler = segment
# docs_site.embed_handler = embed

github = manager.add_github_source('google', 'pigweed', 'main')
github.include = ['pw_tokenizer/*.rst']
github.ignore = ['third_party/*']
github.find()
github.scrape()

# manager.generate()
