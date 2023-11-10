# pigweed-embeddings

## Setup

```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
playwright install --with-deps chromium
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

#### Create the similarity search function

```
create or replace function similarity_search (
    query vector(1536),
    threshold float,
    count int
)
returns table (
    checksum text,
    content text,
    similarity float,
    url text,
    token_count int8
)
language sql stable
as $$
    select
        embeddings.checksum,
        embeddings.content,
        1 - (embeddings.embedding <=> query) as similarity,
        embeddings.url,
        embeddings.token_count
    from embeddings
    where 1 - (embeddings.embedding <=> query) > threshold
    order by similarity desc
    limit count;
$$;
```

## Dev

```
source venv/bin/activate
python3 main.py
deactivate
```

## Notes

* Took 3 mins 22 secs to index pigweed.dev resulting in 1864 rows
  * 3 mins 22 secs = 202 secs
  * 202 / 1864 = 0.11 secs per item
* bazel setup instructions is an example of good regurgitative instructions
* what is pigweed? reply in portuguese
