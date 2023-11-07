# pigweed-embeddings

## Setup

```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
deactivate
```

### Supabase

Create .env

Go to https://supabase.com/dashboard/project/{id}/settings/api

Set `SUPABASE_URL` in `.env` to Project URL

Set `SUPABASE_KEY` in `.env` to `service_role` API key

Go to https://supabase.com/dashboard/project/{id}/database/extensions

Enable `vector` extension for `public` schema

Go to https://supabase.com/dashboard/project/{id}/sql/new

Create following table

```
create table embeddings (
    checksum text primary key,
    embedding vector (1536),
    type text,
    token_count bigint,
    content text,
    url text,
    timestamp bigint
);
```

## Dev

```
source venv/bin/activate
python3 main.py
deactivate
```
