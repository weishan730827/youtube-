import os
import logging
from pathlib import Path
from typing import List, Dict
import yt_dlp

logger = logging.getLogger(__name__)

class SubtitleManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.subtitle_dir = self.base_dir / 'subtitles'
        self.subtitle_dir.mkdir(exist_ok=True)
    
    def get_available_subtitles(self, video_url: str) -> Dict[str, List[str]]:
        """获取可用的字幕列表"""
        try:
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'skip_download': True,
                'quiet': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return {
                    'manual': list(info.get('subtitles', {}).keys()),
                    'automatic': list(info.get('automatic_captions', {}).keys())
                }
        except Exception as e:
            logger.error(f"获取字幕列表失败: {str(e)}")
            return {'manual': [], 'automatic': []}
    
    def download_subtitle(self, video_url: str, lang_code: str, 
                        auto: bool = False) -> str:
        """下载字幕"""
        try:
            output_template = str(self.subtitle_dir / f'%(title)s.%(ext)s')
            ydl_opts = {
                'skip_download': True,
                'quiet': True,
                'outtmpl': output_template,
                'writesubtitles': not auto,
                'writeautomaticsub': auto,
                'subtitleslangs': [lang_code],
                'subtitlesformat': 'srt'
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                base_path = output_template % {'title': info['title'], 'ext': ''}
                subtitle_path = f"{base_path}{lang_code}.srt"
                
                if os.path.exists(subtitle_path):
                    return subtitle_path
                raise FileNotFoundError("字幕文件未找到")
                
        except Exception as e:
            logger.error(f"下载字幕失败: {str(e)}")
            raise

# 创建全局字幕管理器实例
subtitle_manager = SubtitleManager() 