import yt_dlp
import logging
import os

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_download():
    # 检查cookies文件是否存在
    cookies_file = 'cookies.txt'
    if not os.path.exists(cookies_file):
        raise Exception(f"找不到cookies文件: {cookies_file}")
        
    ydl_opts = {
        'quiet': False,
        'verbose': True,
        'proxy': 'http://127.0.0.1:7890',
        'debug': True,
        'cookiefile': cookies_file,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Dest': 'document'
        }
    }
    
    try:
        print("开始测试下载...")
        print(f"使用yt-dlp版本: {yt_dlp.version.__version__}")
        print(f"使用cookies文件: {cookies_file}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            url = "https://youtu.be/cfJzxqf0-DU"
            print(f"正在获取视频信息并下载: {url}")
            
            info = ydl.extract_info(url, download=True)
            print(f"视频标题: {info.get('title', '未知')}")
            
    except Exception as e:
        print(f"错误: {str(e)}")
        logger.error(f"详细错误: {str(e)}")

if __name__ == "__main__":
    test_download()