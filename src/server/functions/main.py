from os import environ
from time import time

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
delimiter = '@&$%&$@&%$@@%&$&&&@%$'

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
    url = data['url']
    text = data['text']
    thread = get_or_create_thread(thread_id)
    assistant = get_or_create_assistant(assistant_id)
    content = f'Summarize {url}\n\n{delimiter}\n\n{text}'
    if len(content) > 32000:
        content = content[0:32000]
    openai.beta.threads.messages.create(thread_id=thread.id, role='user', content=content)
    instructions = f'Summarize the text below the delimiter. The delimiter is {delimiter}.'
    run = openai.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id, instructions=instructions)
    return {
        'thread_id': thread.id,
        'run_id': run.id,
        'assistant_id': assistant.id
    }

def to_markdown(text):
    return markdown(text, extensions=['extra'])

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
        response['message'] = to_markdown(message)
        response['done'] = True
    return response

def remove_context(text, role):
    # Only the user's messages will potentially have context.
    if role != 'user':
        return text
    if delimiter not in text:
        return text
    end = text.index(delimiter)
    return text[0:end]

@app.post('/history')
def history():
    data = request.get_json()
    thread_id = data['thread_id']
    response = {'history': []}
    try:
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
    except Exception as e:
        print(e)
        return response
    for message in messages.data:
        role = message.role
        msg = remove_context(message.content[0].text.value, role)
        if role == 'assistant':
            msg = to_markdown(msg)
        response['history'].append({
            'role': role,
            'message': msg
        })
    response['history'].reverse()
    return response

# TODO: Add exception handling here. Errors originate from here when
# Supabase instance is paused.
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
    msg = f'{message}\n\n{delimiter}\n\n'
    # TODO: Try "IF AND ONLY IF"
    msg += f'Reply to the message above the delimiter. Use the context below the delimiter in your reply. The delimiter is {delimiter}.\n\n'
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
    instructions = f'Reply to the message above the delimiter. Use the context below the delimiter in your reply. The delimiter is {delimiter}.\n\n'
    run = openai.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id, instructions=instructions)
    return {
        'thread_id': thread.id,
        'run_id': run.id,
        'assistant_id': assistant.id
    }

@app.get('/')
def hello_world():
    return f'{int(time())}'

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@https_fn.on_request(timeout_sec=120, memory=options.MemoryOption.GB_4)
def server(req):
    with app.request_context(req.environ):
        return app.full_dispatch_request()
