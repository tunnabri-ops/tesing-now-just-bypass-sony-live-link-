import os
from urllib.parse import urljoin
from flask import Flask, Response, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "SonyLIV Live Proxy is Running!"

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
        if '.m3u8' in target_url or target_url.endswith('.m3u'):
            res = requests.get(target_url, headers=headers, timeout=15)
            content = res.text
            base_proxy_url = request.host_url.rstrip('/') + '/proxy?url='
            
            new_lines = []
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    if not line.startswith('http'):
                        line = urljoin(target_url, line)
                    if 'proxy?url=' not in line:
                        line = base_proxy_url + line
                new_lines.append(line)
            
            updated_playlist = '\n'.join(new_lines)
            
            # ক্যাশিং বন্ধ করার জন্য হেডার যুক্ত করা হলো যাতে লাইভ প্লেলিস্ট রিফ্রেশ হতে পারে
            response = Response(updated_playlist, content_type='application/vnd.apple.mpegurl', status=200)
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response

        # ভিডিওর টুকরোগুলো (.ts) প্রক্সি করার জন্য
        req = requests.get(target_url, headers=headers, stream=True, timeout=15)
        response = Response(
            req.iter_content(chunk_size=1024), 
            content_type=req.headers.get('content-type', 'video/mp2t'),
            status=req.status_code
        )
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
