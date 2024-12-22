from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import yt_dlp
import os
import json
import requests
import logging
from pathlib import Path
from cookie_manager import CookieManager
import browser_cookie3

app = Flask(__name__)
CORS(app)

# 閰嶇疆鏃ュ織
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_proxy():
    """妫€鏌ヤ唬鐞嗚繛鎺ョ姸鎬?""
    try:
        proxies = {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
        }
        r = requests.get('https://www.youtube.com', proxies=proxies, timeout=5)
        return True
    except:
        return False

def get_sogou_cookies_path():
    """鑾峰彇鎼滅嫍娴忚鍣╟ookies璺緞"""
    base_path = os.path.expanduser('~')
    return os.path.join(base_path, 'AppData', 'Roaming', 'SogouExplorer')

def save_cookies(cookies_data):
    """淇濆瓨cookies鏁版嵁"""
    try:
        with open('cookies_netscape.txt', 'w', encoding='utf-8') as f:
            f.write(cookies_data)
        return True
    except Exception as e:
        logger.error(f"淇濆瓨cookies澶辫触: {str(e)}")
        return False

@app.route('/')
def index():
    # 妫€鏌ヤ唬鐞嗙姸鎬?
    proxy_status = check_proxy()
    return render_template('index.html', proxy_status=proxy_status)

@app.route('/api/check-status')
def check_status():
    """妫€鏌ョ郴缁熺姸鎬?""
    try:
        # 妫€鏌ヤ唬鐞?
        proxy_ok = check_proxy()
        
        # 妫€鏌ookies
        cookies_ok = os.path.exists('cookies_netscape.txt')
        
        return jsonify({
            'proxy': proxy_ok,
            'cookies': cookies_ok
        })
    except Exception as e:
        logging.error(f"鐘舵€佹鏌ュけ璐? {str(e)}")
        return jsonify({
            'proxy': False,
            'cookies': False
        })

@app.route('/api/update-cookies', methods=['POST'])
def update_cookies():
    """鏇存柊cookies鐨凙PI鎺ュ彛"""
    try:
        cookies_data = request.form.get('cookies')
        if not cookies_data:
            return jsonify({'error': 'No cookies data provided'}), 400
        
        if save_cookies(cookies_data):
            return jsonify({'message': 'Cookies鏇存柊鎴愬姛'})
        else:
            return jsonify({'error': 'Cookies淇濆瓨澶辫触'}), 500
    except Exception as e:
        logger.error(f"鏇存柊cookies閿欒: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': '璇锋彁渚涜棰慤RL'}), 400
            
        video_url = data['url']
        logger.info(f"锟斤拷锟藉鑾峰彇瑙嗛淇℃伅: {video_url}")
        
        # 鐩存帴浠嶤hrome鑾峰彇cookies
        try:
            cookies = browser_cookie3.chrome(domain_name='youtube.com')
            logger.info("鎴愬姛浠嶤hrome鑾峰彇cookies")
        except Exception as e:
            logger.error(f"浠嶤hrome鑾峰彇cookies澶辫触: {str(e)}")
            cookies = None
        
        # 閰嶇疆yt-dlp閫夐」
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'extract_flat': True,
            'proxy': 'http://127.0.0.1:7890',
            'verbose': True,
            'no_check_certificate': True,
            'cookiesfrombrowser': ('chrome',),  # 鎸囧畾浣跨敤Chrome鐨刢ookies
            'format': 'best',
            'socket_timeout': 30,
            'retries': 3
        }
        
        if cookies:
            cookie_jar = {cookie.name: cookie.value for cookie in cookies if cookie.domain == '.youtube.com'}
            ydl_opts['cookiefile'] = None  # 涓嶄娇鐢╟ookie鏂囦欢
            ydl_opts['cookies'] = cookie_jar
        
        logger.info("姝ｅ湪浣跨敤yt-dlp鑾峰彇淇℃伅...")
        
        # 鑾峰彇瑙嗛淇℃伅
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(video_url, download=False)
                logger.info(f"鎴愬姛鑾峰彇瑙嗛淇℃伅: {info.get('title', '鏈煡')}")
                
                return jsonify({
                    'title': info.get('title', '鏈煡'),
                    'duration': info.get('duration', 0),
                    'size': info.get('filesize', 0)
                })
            except Exception as e:
                logger.error(f"yt-dlp鎻愬彇淇℃伅澶辫触: {str(e)}")
                return jsonify({'error': f'瑙嗛淇℃伅鎻愬彇澶辫触: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"鑾峰彇瑙嗛淇℃伅澶辫触: {str(e)}")
        return jsonify({'error': f'鏈嶅姟鍣ㄩ敊璇? {str(e)}'}), 500

@app.route('/api/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        url = data.get('url')
        format_id = data.get('format_id', 'best')
        
        if not url:
            return jsonify({'error': '璇疯緭鍏RL'}), 400
            
        if not check_proxy():
            return jsonify({'error': 'Clash浠ｇ悊鏈惎鍔ㄦ棤娉曡繛鎺?}), 400
            
        ydl_opts = {
            'format': 'best',
            'merge_output_format': 'mp4',
            'proxy': 'http://127.0.0.1:7890',
            'cookiefile': 'cookies_netscape.txt',  # 浣跨敤cookies鏂囦欢
            'progress_hooks': [progress_hook],
            'outtmpl': '%(title)s.%(ext)s',
            'verbose': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return jsonify({
                'status': 'success',
                'title': info.get('title'),
                'filename': f"{info.get('title')}.mp4"
            })
    except Exception as e:
        logger.error(f"涓嬭浇澶辫触: {str(e)}")
        error_msg = str(e)
        if "Sign in to confirm you're not a bot" in error_msg:
            error_msg = "闇€瑕佹洿鏂癈ookies锛岃鐐瑰嚮涓嬫柟'鏇存柊Cookies'鎸夐挳"
        return jsonify({'error': error_msg}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
