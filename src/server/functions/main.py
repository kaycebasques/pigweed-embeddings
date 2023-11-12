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

@app.post('/retrieve')
def retrieve():
    data = request.get_json()
    thread_id = data['thread_id']
    run_id = data['run_id']
    assistant_id = data['assistant_id']
    status = openai.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
    )
    response = {
        'thread_id': thread_id,
        'run_id': run_id,
        'assistant_id': assistant_id,
        'done': False
    }
    if status.status == 'completed':
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        print(messages['data'])
        print(messages.data[0].content[0].text.value)
        response['done'] = True
    return response

@app.post('/chat')
def chat():
    data = request.get_json()
    query = data['query']
    thread_id = data['thread_id']
    thread = openai.beta.threads.create() if thread_id is None else openai.beta.threads.retrieve(thread_id)
    instructions = 'Help the user build embedded software with Pigweed.'
    assistant = openai.beta.assistants.create(
        name='Pigweed Assistant',
        instructions=instructions,
        tools=[{'type': 'code_interpreter'}],
        model='gpt-4-1106-preview'
    )
    message = openai.beta.threads.messages.create(
        thread_id=thread.id,
        role='user',
        content=query
    )
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=instructions
    )
    return {
        'thread_id': thread.id,
        'run_id': run.id,
        'assistant_id': assistant.id
    }

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
