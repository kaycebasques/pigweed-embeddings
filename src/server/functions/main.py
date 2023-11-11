from firebase_functions import https_fn, options
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.post('/context')
def context():
    data = request.get_json()
    return 'Hello, world!'

@https_fn.on_request(timeout_sec=120, memory=options.MemoryOption.GB_1)
def server(req):
    with app.request_context(req.environ):
        return app.full_dispatch_request()
