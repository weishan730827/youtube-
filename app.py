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

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def progress_hook(d):
    """下载进度回调函数"""
    if d['status'] == 'downloading':
        logger.info(f"下载进度: {d.get('_percent_str', '未知')}")
    elif d['status'] == 'finished':
        logger.info(f"下载完成: {d.get('filename', '未知')}")

def check_proxy():
    """检查代理连接状态"""
    try:
        proxies = {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
        }
        r = requests.get('https://www.youtube.com', proxies=proxies, timeout=5)
        return True
    except:
        return False

def save_cookies(cookies_data):
    """保存cookies数据"""
    try:
        with open('cookies.txt', 'w', encoding='utf-8') as f:
            f.write(cookies_data)
        return True
    except Exception as e:
        logger.error(f"保存cookies失败: {str(e)}")
        return False

@app.route('/')
def index():
    # 检查代理状态
    proxy_status = check_proxy()
    return render_template('index.html', proxy_status=proxy_status)

@app.route('/api/check-status')
def check_status():
    """检查系统状态"""
    try:
        # 检查代理
        proxy_ok = check_proxy()
        
        # 检查cookies
        cookies_ok = os.path.exists('cookies.txt')
        
        return jsonify({
            'proxy': proxy_ok,
            'cookies': cookies_ok
        })
    except Exception as e:
        logging.error(f"状态检查失败: {str(e)}")
        return jsonify({
            'proxy': False,
            'cookies': False
        })

@app.route('/api/update-cookies', methods=['POST'])
def update_cookies():
    """更新cookies的API接口"""
    try:
        cookies_data = request.form.get('cookies')
        if not cookies_data:
            return jsonify({'error': 'No cookies data provided'}), 400
        
        if save_cookies(cookies_data):
            return jsonify({'message': 'Cookies更新成功'})
        else:
            return jsonify({'error': 'Cookies保存失败'}), 500
    except Exception as e:
        logger.error(f"更新cookies错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': '请提供视频URL'}), 400
            
        video_url = data['url']
        logger.info(f"开始获取视频信息: {video_url}")
        
        if not os.path.exists('cookies.txt'):
            return jsonify({'error': '请先更新Cookies'}), 400
        
        # 配置yt-dlp选项
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'extract_flat': True,
            'proxy': 'http://127.0.0.1:7890',
            'verbose': True,
            'no_check_certificate': True,
            'cookiefile': 'cookies.txt',
            'format': 'best',
            'socket_timeout': 30,
            'retries': 3
        }
        
        logger.info("正在使用yt-dlp获取信息...")
        
        # 获取视频信息
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(video_url, download=False)
                logger.info(f"成功获取视频信息: {info.get('title', '未知')}")
                
                return jsonify({
                    'title': info.get('title', '未知'),
                    'duration': info.get('duration', 0),
                    'size': info.get('filesize', 0)
                })
            except Exception as e:
                logger.error(f"yt-dlp提取信息失败: {str(e)}")
                return jsonify({'error': f'视频信息提取失败: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"获取视频信息失败: {str(e)}")
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/api/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        url = data.get('url')
        format_id = data.get('format_id', 'best')
        
        if not url:
            return jsonify({'error': '请输入URL'}), 400
            
        if not check_proxy():
            return jsonify({'error': 'Clash代理未启动无法连接'}), 400
            
        if not os.path.exists('cookies.txt'):
            return jsonify({'error': '请先更新Cookies'}), 400
            
        ydl_opts = {
            'format': 'best',
            'merge_output_format': 'mp4',
            'proxy': 'http://127.0.0.1:7890',
            'cookiefile': 'cookies.txt',
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
        logger.error(f"下载失败: {str(e)}")
        error_msg = str(e)
        if "Sign in to confirm you're not a bot" in error_msg:
            error_msg = "需要更新Cookies，请点击下方'更新Cookies'按钮"
        return jsonify({'error': error_msg}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)