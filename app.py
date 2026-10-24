import os
from flask import Flask, Response, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "SonyLIV Smart Proxy Server is Running!"

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
        # যদি লিংকটি m3u বা m3u8 প্লেলিস্ট হয়, তবে প্রসেস করে পাঠাবে
        if target_url.endswith('.m3u') or target_url.endswith('.m3u8'):
            res = requests.get(target_url, headers=headers, timeout=15)
            content = res.text
            
            # সার্ভারের বেস ইউরল বের করা
            base_proxy_url = request.host_url.rstrip('/') + '/proxy?url='
            
            # এমথ্রিইউ ফাইলের লাইনগুলো চেক করে স্ট্রিম লিংকের সাথে প্রক্সি যুক্ত করা
            new_lines = []
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    # যদি লিংকে ইতিমধ্যে প্রক্সি না থাকে
                    if 'proxy?url=' not in line:
                        line = base_proxy_url + line
                new_lines.append(line)
            
            updated_playlist = '\n'.join(new_lines)
            return Response(updated_playlist, content_type='audio/x-mpegurl', status=200)

        # সাধারণ ভিডিও স্ট্রিম হলে সরাসরি প্রক্সি করবে
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
