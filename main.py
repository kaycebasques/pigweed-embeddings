import os
import json

import bs4
import mbedmgr
import dotenv

import docs_handlers
import github_handlers
import database

def main():
    # Init
    dotenv.load_dotenv()

    db = database.Database()
    checksums = db.get_checksums()

    # Central manager that coordinates the other managers
    manager = mbedmgr.EmbeddingsManager(checksums)

    # Official docs manager
    docs = manager.add_website_source(source_id='https://pigweed.dev')
    docs.scrape_urls_from_sitemap('https://pigweed.dev/sitemap.xml')
    docs.scrape()
    docs.set_preprocess_handler(docs_handlers.preprocess)
    docs.set_segment_handler(docs_handlers.segment)
    docs.set_embed_handler(docs_handlers.embed)

    # GitHub source code manager
    include = ['*.h', '*.cc', '*.c']
    exclude = ['third_party/*']
    github = manager.add_github_source('https://github.com/google/pigweed', 'google', 'pigweed', 'main', include, exclude)
    github.set_embed_handler(github_handlers.embed)

    # Generate embeddings for all the sources!
    manager.generate()

    # Now that the timestamps have been refreshed, we have a better idea
    # about which embeddings are stale and can be removed.
    db.prune()

if __name__ == '__main__':
    main()
