import os

import openai
import dotenv
import supabase

# Init.
dotenv.load_dotenv()
database = supabase.create_client(
    supabase_url=os.environ.get('SUPABASE_URL'),
    supabase_key=os.environ.get('SUPABASE_KEY')
)
openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_KEY'))

# Get query and generate into embedding.
print()
query = input()
print()
embedding = openai_client.embeddings.create(
    input=query,
    model='text-embedding-ada-002'
).data[0].embedding

# Get docs related to the query.
prompt = f'Reply to this input from the user: {query}\n\n'
prompt += 'The rest of this prompt is context that should be used in your reply.\n\n'
supabase_response = database.rpc('similarity_search', {'query': embedding, 'threshold': 0.7, 'count': 3}).execute()
for item in supabase_response.data:
    content = item['content']
    url = item['url']
    prompt += f'{content}\n\n'
    prompt += f'{url}\n\n'

# Generate a reply.
openai_response = openai_client.chat.completions.create(
    model='gpt-4-1106-preview',
    messages=[
        {'role': 'user', 'content': prompt}
    ]
)
reply = openai_response.choices[0].message.content
print(reply)