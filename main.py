import mbedmgr
import json

manager = mbedmgr.EmbeddingsManager()
docs_site = manager.add_website_source(source_id='pigweed_dev')
docs_site.scrape_sitemap('https://pigweed.dev/sitemap.xml')
docs_site.scrape_urls()
