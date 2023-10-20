import mbedmgr
import json

sitemap_url = 'https://pigweed.dev/sitemap.xml'
embeddings_manager = mbedmgr.EmbeddingsManager()
urls = embeddings_manager.scrape_sitemap(sitemap_url)
data = embeddings_manager.scrape_urls(urls)
print(json.dumps(data, indent=4))
