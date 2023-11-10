import os
import threading

import requests
import bs4
import openai
import playwright.sync_api as playwright

import database
import utilities

def get_urls():
    url_pattern = 'https://issues.pigweed.dev/issues?q=status:open&p={}'
    urls = []
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # TODO: The magic number 25 is based on me just checking how many
        # pages of open bugs there are. Maybe we should have an automated
        # way of detecting this...
        for page_number in range(3):
            url = url_pattern.format(page_number)
            # TODO: Switch to multi-threaded impl...
            page.goto(url, wait_until='networkidle')
            html = page.content()
            soup = bs4.BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a'):
                href = a.get('href')
                if href is None:
                    continue
                if href.startswith('issues/'):
                    urls.append(f'https://issues.pigweed.dev/{href}')
        page.close()
        browser.close()
    return urls

def preprocess(url, mgr):
    page = mgr.get_page(url)
    text = page['text']
    soup = bs4.BeautifulSoup(text, 'html.parser')
    body = soup.find('body')
    for tag_name in ['script', 'style', 'link']:
        for useless_tag in body.find_all(tag_name):
            useless_tag.decompose()
    mgr.set_page(url, str(body))