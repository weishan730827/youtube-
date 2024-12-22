import yt_dlp
import time
import os

class MyLogger:
    def debug(self, msg):
        if msg.startswith('[download]'): 
            print(msg)
    
    def info(self, msg):
        print(msg)
    
    def warning(self, msg):
        print(f"警告: {msg}")
    
    def error(self, msg):
        print(f"错误: {msg}")

def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"\r下载中... {d.get('_percent_str', '0%')} "
              f"速度: {d.get('_speed_str', 'N/A')} "
              f"剩余时间: {d.get('_eta_str', 'N/A')}", end='')
    elif d['status'] == 'finished':
        print(f"\n下载完成！总大小: {d.get('_total_bytes_str', 'N/A')}")

def download_video():
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'proxy': 'http://127.0.0.1:7890',
        'format': 'best',
        'merge_output_format': 'mp4',
        'cookiefile': 'cookies_netscape.txt',
        'verbose': True,
        'outtmpl': '%(title)s.%(ext)s',
        'progress': True,
        'progress_hooks': [progress_hook],
        'logger': MyLogger(),
        'no_color': True,
        'socket_timeout': 60,
        'retries': 5,
        'ignoreerrors': True,
        'no_check_certificate': True,
        'fragment_retries': 10,
        'buffersize': 1024*1024,
        'http_chunk_size': 10485760,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    
    try:
        print("=== YouTube 视频下载器 ===")
        print("开始下载视频...")
        print(f"使用yt-dlp版本: {yt_dlp.version.__version__}")
        print("=" * 50)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            url = input("请输入YouTube视频URL: ")
            print("\n正在获取视频信息...")
            print("=" * 50)
            
            info = ydl.extract_info(url, download=False)
            if info:
                print(f"\n视频标题: {info.get('title', 'Unknown')}")
                print(f"视频时长: {int(info.get('duration', 0)/60)}分{int(info.get('duration', 0)%60)}秒")
                print(f"视频质量: {info.get('format', 'Unknown')}")
                print(f"预计大小: {info.get('filesize_approx', 0) / 1024 / 1024:.2f}MB")
                print("=" * 50)
                
                confirm = input("\n是否开始下载? (y/n): ")
                if confirm.lower() == 'y':
                    print("\n开始下载...")
                    print("=" * 50)
                    info = ydl.extract_info(url, download=True)
                    print("\n下载完成!")
                    print(f"保存位置: {os.path.abspath(info.get('title', 'video') + '.' + info.get('ext', 'mp4'))}")
                else:
                    print("已取消下载")
            
    except Exception as e:
        print(f"下载失败: {str(e)}")
        if hasattr(e, 'msg'):
            print(f"详细错误: {e.msg}")

if __name__ == "__main__":
    download_video() 