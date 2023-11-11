if [ ! -f "src/embeddings/.env" ]; then
    echo "ERROR: //src/embeddings/.env not found"
    echo "1. Create //src/embeddings/.env"
    echo "2. Set OPENAI_KEY to OpenAI API Key"
    echo "3. Set SUPABASE_KEY to service_role Project API Key"
    echo "4. Set SUPABASE_URL to Project URL"
    echo "Note: this script copies //src/embeddings/.env to //src/server/functions/.env"
    exit 1
fi

cp src/embeddings/.env src/server/functions/.env
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
deactivate
