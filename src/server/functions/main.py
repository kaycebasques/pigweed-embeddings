from dotenv import load_dotenv
from firebase_functions import https_fn, options
from flask import Flask, request
from flask_cors import CORS
from openai import OpenAI
from supabase import create_client

import openai
import dotenv
import supabase

# Init.
load_dotenv()
database = supabase.create_client(
    supabase_url=os.environ.get('SUPABASE_URL'),
    supabase_key=os.environ.get('SUPABASE_KEY')
)
openai = OpenAI(api_key=os.environ.get('OPENAI_KEY'))
app = Flask(__name__)
CORS(app)

@app.get('/context')  # DEBUG: Change back to post
def context():
    data = request.get_json()
    return 'Hello, world!'

@https_fn.on_request(timeout_sec=120, memory=options.MemoryOption.GB_1)
def server(req):
    with app.request_context(req.environ):
        return app.full_dispatch_request()
