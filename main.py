import os
import json

import bs4
import mbedmgr
import dotenv

import docs_manager
import github_manager
import bugs_manager

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

    # Bugs manager
    bugs = manager.add_website_source(source_id='issues.pigweed.dev')
    bug_urls = bugs_manager.get_urls()
    bugs.pages = bug_urls
    bugs.scrape_handler = bugs_manager.scrape
    # TODO create preprocess handler that narrows down to article[role="main"]
    bugs.segment_handler = False
    bugs.embed_handler = False
    print(json.dumps(bugs.pages, indent=4))

    # GitHub source code manager
    # github = manager.add_github_source('google', 'pigweed', 'main')
    # github.include = ['*.h']
    # github.ignore = ['third_party/*']
    # github.embed_handler = github_manager.embed

    # Generate embeddings for all the sources!
    manager.generate()

if __name__ == '__main__':
    main()
