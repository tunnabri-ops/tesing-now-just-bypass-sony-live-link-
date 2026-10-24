# ১. যদি ফাইলটি .m3u বা .m3u8 প্লেলিস্ট হয়
        if '.m3u' in target_url or '.m3u8' in target_url:
            res = requests.get(target_url, headers=headers, timeout=15)
            content = res.text
            base_proxy_url = request.host_url.rstrip('/') + '/proxy?url='
            
            new_lines = []
            lines = content.splitlines()
            skip_next = False
            
            for i, line in enumerate(lines):
                line = line.strip()
                # যদি মাস্টার প্লেলিস্ট হয় এবং 720p ফিল্টার করতে চান
                if 'RESOLUTION=' in line and '1280x720' not in line:
                    # অন্য রেজুলেশনগুলো স্কিপ করার লজিক (ঐচ্ছিক)
                    pass
                
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
