import os
import json

import bs4
import mbedmgr
import dotenv

import docs_manager
import github_manager
import bugs_manager
import database

def main():
    # Init
    dotenv.load_dotenv()

    # Central manager that coordinates the other managers
    manager = mbedmgr.EmbeddingsManager()

    # Official docs manager
    # docs_site = manager.add_website_source(source_id='pigweed.dev')
    # docs_site.sitemap = 'https://pigweed.dev/sitemap.xml'
    # docs_site.preprocess_handler = docs_manager.preprocess
    # docs_site.segment_handler = docs_manager.segment
    # docs_site.embed_handler = docs_manager.embed

    # GitHub source code manager
    # github = manager.add_github_source('google', 'pigweed', 'main')
    # github.include = ['*.h']
    # github.ignore = ['third_party/*']
    # github.embed_handler = github_manager.embed

    # Generate embeddings for all the sources!
    # manager.generate()

    db = database.Database()
    db.prune()

if __name__ == '__main__':
    main()
