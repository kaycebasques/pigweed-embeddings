# Make sure that env vars file exists.
if [ ! -f "src/embeddings/.env" ]; then
    echo "ERROR: //src/embeddings/.env not found"
    echo "1. Create //src/embeddings/.env"
    echo "2. Set OPENAI_KEY to OpenAI API Key"
    echo "3. Set SUPABASE_KEY to service_role Project API Key"
    echo "4. Set SUPABASE_URL to Project URL"
    echo "Note: this script copies //src/embeddings/.env to //src/server/functions/.env"
    return
fi
# TODO: Check that all env vars exist.
cp src/embeddings/.env src/server/functions/.env

# Set up virtual env for generating embeddings.
python3 -m venv src/embeddings/venv
source src/embeddings/venv/bin/activate
python3 -m pip install -r src/embeddings/requirements.txt
deactivate

# Set up virtual env for running the server.
python3 -m venv src/server/functions/venv
source src/server/functions/venv/bin/activate
python3 -m pip install -r src/server/functions/requirements.txt
deactivate
