import os
from flask import Flask, Response, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "SonyLIV Proxy Server is Running!"

@app.route('/proxy')
def proxy_stream():
    target_url = request.args.get('url')
    if not target_url:
        return "URL is required", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.sonyliv.com/'
    }

    try:
        req = requests.get(target_url, headers=headers, stream=True, timeout=15)
        return Response(
            req.iter_content(chunk_size=1024), 
            content_type=req.headers.get('content-type', 'video/mp2t'),
            status=req.status_code
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
