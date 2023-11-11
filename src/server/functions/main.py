from os import environ

from dotenv import load_dotenv
from firebase_functions import https_fn, options
from flask import Flask, request
from flask_cors import CORS
from openai import OpenAI
from supabase import create_client

# Init.
load_dotenv()
database = create_client(
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
    return 'Hello, world!'

@https_fn.on_request(timeout_sec=120, memory=options.MemoryOption.GB_1)
def server(req):
    with app.request_context(req.environ):
        return app.full_dispatch_request()
