import os

import openai

import database
import utilities

# TODO need the URL not the path
def embed(mgr, path, text, checksums):
    print('in correct embed')
    print(path)
    return
    openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_KEY'))
    db = database.Database()
    if utilities.token_count(content) > utilities.max_token_count():
        return
    if db.row_exists(content=content):
        db.update_timestamp(content=content)
    else:
        embedding = openai_client.embeddings.create(
            input=content,
            model=utilities.embedding_model()
        ).data[0].embedding
        db.add(content=content, content_type='code', url=url, embedding=embedding)
