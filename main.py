import typing
import hashlib
import json

import bs4
import tiktoken
import mbedmgr

token_encoder = tiktoken.get_encoding('cl100k_base')
max_token_count = 8191

class WebpageData(typing.TypedDict):
    text: str

def preprocess(url: str, data: typing.Dict[str, WebpageData]) -> None:
    soup = bs4.BeautifulSoup(data[url]['text'], 'html.parser')
    main = soup.select('div.main')[0]
    for script in main.find_all('script'):
        script.decompose()
    for style in main.find_all('style'):
        style.decompose()
    for link in main.find_all('link'):
        link.decompose()
    data[url]['text'] = str(main)

# TODO: Store segments in database at this point?
def segment(url: str, data: typing.Dict[str, WebpageData]) -> None:
    soup = bs4.BeautifulSoup(data[url]['text'], 'html.parser')
    sections = []
    for section in soup.find_all('section'):
        sections.append(str(section))
    data[url]['sections'] = sections

def embed(url: str, data: typing.Dict[str, WebpageData]) -> None:
    for section in data[url]['sections']:
        checksum = hashlib.md5(section.encode('utf-8')).hexdigest()
        token_count = len(token_encoder.encode(section))
        print(f'{checksum} - {token_count}')

manager = mbedmgr.EmbeddingsManager()

docs_site = manager.add_website_source(source_id='https://pigweed.dev')
docs_site.get_pages_from_sitemap('https://pigweed.dev/sitemap.xml')
docs_site.preprocess_handler = preprocess
docs_site.segment_handler = segment
docs_site.embed_handler = embed

manager.generate()
