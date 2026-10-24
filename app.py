import os
import json
from urllib.parse import urljoin
from flask import Flask, Response, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "SonyLIV Universal Proxy Server is Running!"

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
        # ১. যদি ফাইলটি .m3u বা .m3u8 প্লেলিস্ট হয়
        if '.m3u' in target_url or '.m3u8' in target_url:
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
            response = Response(updated_playlist, content_type='application/vnd.apple.mpegurl', status=200)
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Access-Control-Allow-Origin"] = "*"
            return response

        # ২. যদি ফাইলটি .json প্লেলিস্ট হয়
        elif '.json' in target_url:
            res = requests.get(target_url, headers=headers, timeout=15)
            try:
                data = res.json()
                base_proxy_url = request.host_url.rstrip('/') + '/proxy?url='
                
                # JSON এর ভেতরের সব লিংকের সাথে প্রক্সি যুক্ত করার ফাংশন
                def update_json_urls(obj):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if k in ['url', 'link', 'stream', 'stream_url'] and isinstance(v, str) and v.startswith('http'):
                                if 'proxy?url=' not in v:
                                    obj[k] = base_proxy_url + v
                            else:
                                update_json_urls(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            update_json_urls(item)
                    return obj

                updated_data = update_json_urls(data)
                response = Response(json.dumps(updated_data), content_type='application/json', status=200)
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Access-Control-Allow-Origin"] = "*"
                return response
            except Exception:
                response = Response(res.text, content_type='application/json', status=200)
                response.headers["Access-Control-Allow-Origin"] = "*"
                return response

        # ৩. ভিডিওর ছোট টুকরো (.ts বা অন্যান্য মিডিয়া ফাইল) প্রক্সি করার জন্য
        req = requests.get(target_url, headers=headers, stream=True, timeout=15)
        response = Response(
            req.iter_content(chunk_size=1024), 
            content_type=req.headers.get('content-type', 'video/mp2t'),
            status=req.status_code
        )
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
