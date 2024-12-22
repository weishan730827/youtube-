import yt_dlp
import time

def download_video():
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'proxy': 'http://127.0.0.1:7890',
        'format': '22/best',
        'cookiefile': 'cookies.txt',
        'verbose': True,
        'outtmpl': '%(title)s.%(ext)s',
        'progress': True,
        'no_color': True,
        'socket_timeout': 30,
        'retries': 3,
        'ignoreerrors': True,
        'no_check_certificate': True
    }
    
    try:
        print("开始下载视频...")
        print(f"使用yt-dlp版本: {yt_dlp.version.__version__}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            print(f"正在获取视频信息: {url}")
            time.sleep(2)
            
            print("尝试获取视频信息...")
            info = ydl.extract_info(url, download=False)
            if info:
                print(f"成功获取视频信息: {info.get('title', 'Unknown')}")
                print("开始下载...")
                info = ydl.extract_info(url, download=True)
                print(f"\n下载完成!")
                print(f"视频标题: {info.get('title', 'Unknown')}")
                print(f"文件名: {info.get('title', 'video')}.{info.get('ext', 'mp4')}")
            
    except Exception as e:
        print(f"下载失败: {str(e)}")
        if hasattr(e, 'msg'):
            print(f"详细错误: {e.msg}")

if __name__ == "__main__":
    download_video()