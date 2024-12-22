import os
import json
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).parent.absolute()

# 默认配置
DEFAULT_CONFIG = {
    'proxy': {
        'enabled': True,
        'host': '127.0.0.1',
        'port': 7890,
        'username': None,
        'password': None
    },
    'download': {
        'output_dir': str(BASE_DIR / 'downloads'),
        'format': 'best[ext=mp4]/best',
        'max_retries': 3,
        'timeout': 30
    },
    'server': {
        'host': '0.0.0.0',
        'port': 8080
    }
}

class Config:
    def __init__(self):
        self.config_file = BASE_DIR / 'config.json'
        self.load_config()

    def load_config(self):
        """加载配置文件，如果不存在则创建默认配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = DEFAULT_CONFIG
                self.save_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self.settings = DEFAULT_CONFIG

    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def get_proxy_url(self):
        """获取代理URL"""
        if not self.settings['proxy']['enabled']:
            return None
            
        proxy = self.settings['proxy']
        auth = ''
        if proxy['username'] and proxy['password']:
            auth = f"{proxy['username']}:{proxy['password']}@"
        return f"http://{auth}{proxy['host']}:{proxy['port']}"

    def get_yt_dlp_opts(self):
        """获取yt-dlp配置选项"""
        return {
            'format': self.settings['download']['format'],
            'outtmpl': os.path.join(
                self.settings['download']['output_dir'], 
                '%(title)s.%(ext)s'
            ),
            'proxy': self.get_proxy_url(),
            'socket_timeout': self.settings['download']['timeout'],
            'retries': self.settings['download']['max_retries'],
            'quiet': False,
            'verbose': True,
            'nocheckcertificate': True,
            'no_warnings': False,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'player_skip': ['webpage', 'config', 'js'],
                }
            }
        }

# 创建全局配置实例
config = Config() 