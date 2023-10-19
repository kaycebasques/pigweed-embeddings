import mbedmgr

sitemap_url = 'https://pigweed.dev/sitemap.xml'
embeddings_manager = mbedmgr.EmbeddingsManager()
print(embeddings_manager.scrape_sitemap(sitemap_url))
