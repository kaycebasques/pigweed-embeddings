import mbedmgr
import json
import bs4

manager = mbedmgr.EmbeddingsManager()

docs_site = manager.add_website_source(source_id='pigweed_dev')
docs_site.get_pages_from_sitemap('https://pigweed.dev/sitemap.xml')
docs_site.scrape_pages()
docs_site.minify_pages()
docs_site.save()
