from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import yt_dlp
from urllib.parse import unquote
import logging
import os
import browser_cookie3
import requests
import time

# 设置详细的日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_proxy():
    """检查代理连接"""
    proxy = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }
    try:
        r = requests.get('https://www.youtube.com', proxies=proxy, timeout=5)
        return r.status_code == 200
    except Exception as e:
        logger.error(f"代理检查失败: {str(e)}")
        return False

class VideoDownloader(BaseHTTPRequestHandler):
    def do_GET(self):
        # 添加请求头调试
        logger.debug(f"收到GET请求: {self.path}")
        
        # 检查代理
        if not check_proxy():
            logger.error("代理连接不可用")
            self.send_error_json(500, "代理连接不可用，请检查Clash是否正常运行")
            return
            
        try:
            if self.path == '/':
                with open('templates/index.html', 'r', encoding='utf-8') as f:
                    html = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
                return
                
            if self.path.startswith('/api/video-info/'):
                try:
                    video_url = unquote(self.path.split('/api/video-info/')[1])
                    logger.info(f"正在获取视频信息，URL: {video_url}")
                    
                    # 添加重试机制
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            ydl_opts = {
                                'quiet': True,
                                'no_warnings': True,
                                'extract_flat': False,
                                'cookiesfrombrowser': ('chrome',),
                                'proxy': 'http://127.0.0.1:7890',
                            }
                            
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                logger.info(f"尝试第 {attempt + 1} 次获取视频信息...")
                                info = ydl.extract_info(video_url, download=False)
                                formats = self._parse_formats(info.get('formats', []))
                                
                                response = {
                                    'title': info.get('title', '未知标题'),
                                    'formats': formats
                                }
                                
                                self.send_response(200)
                                self.send_header('Content-type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()
                                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                                logger.info(f"成功获取视频信息: {info.get('title', '未知标题')}")
                                # 如果成功，跳出重试循环
                                break
                        except Exception as e:
                            if attempt == max_retries - 1:  # 最后一次尝试
                                raise
                            logger.warning(f"第 {attempt + 1} 次尝试失败，等待重试...")
                            time.sleep(2)  # 等待2秒后重试
                except Exception as e:
                    logger.error(f"获取视频信息失败: {str(e)}")
                    self.send_error_json(400, f"获取视频信息失败: {str(e)}")
                return
        except Exception as e:
            logger.error(f"处理GET请求失败: {str(e)}")
            self.send_error_json(500, f"服务器错误: {str(e)}")

    def do_POST(self):
        try:
            if self.path == '/api/download':
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    try:
                        data = json.loads(post_data.decode('utf-8'))
                        url = data.get('url')
                        format_id = data.get('format_id', 'best')
                        
                        if not url:
                            raise ValueError("URL不能为空")
                        
                        logger.info(f"开始下载视频: {url}, 格式: {format_id}")
                        
                        if not os.path.exists('downloads'):
                            os.makedirs('downloads')
                            logger.info("创建下载目录: downloads")
                        
                        ydl_opts = {
                            'format': format_id,
                            'outtmpl': 'downloads/%(title)s.%(ext)s',
                            'progress_hooks': [self._progress_hook],
                            'cookiesfrombrowser': ('chrome',),
                            'proxy': 'http://127.0.0.1:7890',  # Clash 默认 HTTP 代理端口
                        }
                        
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(url)
                            
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'status': 'success',
                            'title': info.get('title', '未知标题')
                        }, ensure_ascii=False).encode('utf-8'))
                        logger.info(f"视频下载完成: {info.get('title', '未知标题')}")
                    except Exception as e:
                        logger.error(f"下载失败: {str(e)}")
                        self.send_error_json(400, f"下载失败: {str(e)}")
                else:
                    logger.error("请求数据为空")
                    self.send_error_json(400, "请求数据为空")
                return
        except Exception as e:
            logger.error(f"处理POST请求失败: {str(e)}")
            self.send_error_json(500, f"服务器错误: {str(e)}")

    def send_error_json(self, code, message):
        """发送JSON格式的错误响应"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'error': message
        }, ensure_ascii=False).encode('utf-8'))

    def _parse_formats(self, formats):
        """解析视频格式"""
        parsed = []
        for f in formats:
            if f.get('vcodec', 'none') != 'none' and f.get('acodec', 'none') != 'none':
                parsed.append({
                    'format_id': f['format_id'],
                    'ext': f.get('ext', 'unknown'),
                    'resolution': f.get('resolution', 'unknown'),
                    'filesize': f.get('filesize', 0),
                    'note': f.get('format_note', '')
                })
        return parsed

    def _progress_hook(self, d):
        """下载进度回调"""
        if d['status'] == 'downloading':
            logger.info(f"下载进度: {d.get('_percent_str', '0%')}")
        elif d['status'] == 'finished':
            logger.info(f"下载完成: {d['filename']}")

def run(server_class=HTTPServer, handler_class=VideoDownloader, port=8000):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        logger.info("创建下载目录: downloads")
        
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logger.info(f'启动服务器在端口 {port}...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('服务器关闭...')
        httpd.server_close()

if __name__ == '__main__':
    run()