import mbedmgr
import json
import bs4
import typing
import uuid  # DEBUG

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

def segment(url: str, data: typing.Dict[str, WebpageData]) -> None:
    soup = bs4.BeautifulSoup(data[url]['text'], 'html.parser')
    sections = []
    for section in soup.find_all('section'):
        sections.append(str(section))
    data[url]['sections'] = sections

manager = mbedmgr.EmbeddingsManager()

docs_site = manager.add_website_source(source_id='https://pigweed.dev')
docs_site.get_pages_from_sitemap('https://pigweed.dev/sitemap.xml')
docs_site.preprocess_handler = preprocess
docs_site.segment_handler = segment

manager.generate()

for section in docs_site.data['https://pigweed.dev/docker/docs.html']['sections']:
    print(section)
    print()
    print()
