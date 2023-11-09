import hashlib
import time

import tiktoken

def checksum(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def token_count(content):
    token_encoder = tiktoken.get_encoding('cl100k_base')
    return len(token_encoder.encode(content))

def timestamp():
    return int(time.time())
