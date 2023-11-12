from os import environ

from dotenv import load_dotenv
from firebase_functions import https_fn, options
from flask import Flask, request
from flask_cors import CORS
from markdown import markdown
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

def get_chat_model():
    return 'gpt-4-1106-preview'

def get_embedding_model():
    return 'text-embedding-ada-002'

def get_or_create_assistant(assistant_id):
    if assistant_id is None:
        name = 'Pigweed Assistant'
        instructions = 'Help the user develop embedded software with Pigweed.'
        model = get_chat_model()
        return openai.beta.assistants.create(name=name, instructions=instructions, model=model)
    else:
        return openai.beta.assistants.retrieve(assistant_id)

def get_or_create_thread(thread_id):
    if thread_id is None:
        return openai.beta.threads.create()
    else:
        return openai.beta.threads.retrieve(thread_id)

@app.post('/summarize')
def summarize():
    data = request.get_json()
    thread_id = data['thread_id']
    assistant_id = data['assistant_id']
    text = data['text']
    # TODO: Divide and conquer the huge texts with recursive summaries...
    if len(text) > 32768:
        text = text[0:32765]
    thread = get_or_create_thread(thread_id)
    assistant = get_or_create_assistant(assistant_id)
    openai.beta.threads.messages.create(thread_id=thread.id, role='user', content=text)
    instructions = 'Summarize the text that the user provided.'
    run = openai.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id, instructions=instructions)
    return {
        'thread_id': thread.id,
        'run_id': run.id,
        'assistant_id': assistant.id
    }

@app.post('/retrieve')
def retrieve():
    data = request.get_json()
    thread_id = data['thread_id']
    run_id = data['run_id']
    run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
    response = {'thread_id': thread_id, 'run_id': run_id, 'done': False}
    if run.status == 'completed':
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        message = messages.data[0].content[0].text.value
        response['message'] = markdown(message, extensions=['extra'])
        response['done'] = True
    return response

@app.post('/chat')
def chat():
    data = request.get_json()
    message = data['message']
    message_with_context = create_message_with_context(message)
    thread_id = data['thread_id']
    assistant_id = data['assistant_id']
    thread = get_or_create_thread(thread_id)
    assistant = get_or_create_assistant(assistant_id)
    openai.beta.threads.messages.create(thread_id=thread.id, role='user', content=message_with_context)
    instructions = "Reply to the user's message. Reference the context that is provided below the user's message."
    run = openai.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id, instructions=instructions)
    return {
        'thread_id': thread.id,
        'run_id': run.id,
        'assistant_id': assistant.id
    }

def create_message_with_context(message):
    model = get_embedding_model()
    embedding_response = openai.embeddings.create(input=message, model=model)
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
    msg = f'Reply to the following message from the user:\n\n{message}\n\n'
    msg += 'Reference the following context in your reply:\n\n'
    max_length = 32000
    for item in database_response.data:
        content = item['content']
        url = item['url']
        actual_length = len(msg) + len(content) + len(url)
        if actual_length > max_length:
            continue
        msg += f"{item['content']}\n\n"
        msg += f"{item['url']}\n\n"
    return msg

@app.get('/')
def hello_world():
    print(environ.get('SUPABASE_URL'))
    print(environ.get('SUPABASE_KEY'))
    print(environ.get('OPENAI_KEY'))
    return 'Hello, world!'

@https_fn.on_request(timeout_sec=120, memory=options.MemoryOption.GB_4)
def server(req):
    with app.request_context(req.environ):
        return app.full_dispatch_request()
