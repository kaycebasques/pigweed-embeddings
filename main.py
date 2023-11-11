import os
import json

import bs4
import mbedmgr
import dotenv

import docs_manager
import github_handlers
import bugs_manager
import database

def main():
    # Init
    dotenv.load_dotenv()

    db = database.Database()
    checksums = db.get_checksums()

    # Central manager that coordinates the other managers
    manager = mbedmgr.EmbeddingsManager()
    manager.set_checksums(checksums)

    # Official docs manager
    # docs_site = manager.add_website_source(source_id='pigweed.dev')
    # docs_site.set_sitemap('https://pigweed.dev/sitemap.xml')
    # docs_site.scrape_pages_from_sitemap()
    # docs_site.set_preprocess_handler(docs_manager.preprocess)
    # docs_site.set_segment_handler(docs_manager.segment)
    # docs_site.set_embed_handler(docs_manager.embed)

    # GitHub source code manager
    include = ['*.h']
    exclude = ['third_party/*']
    github_manager = manager.add_github_source('google', 'pigweed', 'main', include, exclude)
    github_manager.set_embed_handler(github_handlers.embed)

    # Generate embeddings for all the sources!
    # manager.generate()

    # db.prune()

if __name__ == '__main__':
    main()
