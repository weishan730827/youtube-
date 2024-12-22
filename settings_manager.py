import json
import logging
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class VideoFormat:
    format_id: str
    ext: str
    resolution: str
    filesize: int
    note: str = ""

@dataclass
class SystemSettings:
    max_concurrent_downloads: int = 2
    default_video_quality: str = 'best'
    download_path: str = 'downloads'
    enable_proxy: bool = True
    proxy_url: str = 'http://127.0.0.1:7890'
    auto_delete_completed: bool = False
    delete_after_days: int = 7
    max_retries: int = 3
    chunk_size: int = 8192
    user_agent: str = 'Mozilla/5.0'

class SettingsManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.settings_file = self.base_dir / 'settings.json'
        self.settings = SystemSettings()
        self.load_settings()
    
    def load_settings(self):
        """从文件加载设置"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.settings, key):
                            setattr(self.settings, key, value)
                logger.info("成功加载设置")
        except Exception as e:
            logger.error(f"加载设置失败: {str(e)}")
    
    def save_settings(self):
        """保存设置到文件"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, indent=4, ensure_ascii=False)
            logger.info("成功保存设置")
        except Exception as e:
            logger.error(f"保存设置失败: {str(e)}")
    
    def update_settings(self, settings: Dict[str, Any]):
        """更新设置"""
        for key, value in settings.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        self.save_settings()
    
    def get_settings(self) -> Dict[str, Any]:
        """获取当前设置"""
        return asdict(self.settings)

# 创建全局设置管理器实例
settings_manager = SettingsManager() 