from os import environ

from dotenv import load_dotenv
from firebase_functions import https_fn, options
from flask import Flask, request
from flask_cors import CORS
from openai import OpenAI
from supabase import create_client

load_dotenv()
supabase = create_client(
    supabase_url=environ.get('SUPABASE_URL'),
    supabase_key=environ.get('SUPABASE_KEY')
)
openai = OpenAI(api_key=environ.get('OPENAI_KEY'))
app = Flask(__name__)
CORS(app)

@app.get('/')
def hello_world():
    return 'Hello, world!'

@app.post('/context')
def context():
    data = request.get_json()
    query = data['query']
    model = 'text-embedding-ada-002'
    embedding_response = openai.embeddings.create(input=query, model=model)
    embedding = embedding_response.data[0].embedding
    database_response = supabase.rpc(
        'similarity_search',
        {
            'query': embedding,
            'threshold': 0.6,
            'count': 1000
        }
    ).execute()
    items = []
    for item in database_response.data:
        items.append({
            'content': item['content'],
            'url': item['url'],
            'token_count': item['token_count']
        })
    return {'context': items}

@https_fn.on_request(timeout_sec=120, memory=options.MemoryOption.GB_1)
def server(req):
    with app.request_context(req.environ):
        return app.full_dispatch_request()
