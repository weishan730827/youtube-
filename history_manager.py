import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class DownloadRecord:
    id: str
    url: str
    title: str
    format: str
    size: int
    path: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    subtitles: List[str] = None

class HistoryManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.history_file = self.base_dir / 'download_history.json'
        self.history: List[DownloadRecord] = []
        self.load_history()
    
    def load_history(self):
        """从文件加载历史记录"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = [DownloadRecord(**record) for record in data]
                logger.info(f"已加载 {len(self.history)} 条历史记录")
        except Exception as e:
            logger.error(f"加载历史记录失败: {str(e)}")
            self.history = []
    
    def save_history(self):
        """保存历史记录到文件"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(record) for record in self.history], f, 
                         indent=4, ensure_ascii=False)
            logger.info("历史记录已保存")
        except Exception as e:
            logger.error(f"保存历史记录失败: {str(e)}")
    
    def add_record(self, record: Dict) -> DownloadRecord:
        """添加新的下载记录"""
        record['created_at'] = datetime.now().isoformat()
        download_record = DownloadRecord(**record)
        self.history.insert(0, download_record)
        self.save_history()
        return download_record
    
    def update_record(self, id: str, **kwargs) -> Optional[DownloadRecord]:
        """更新下载记录"""
        for record in self.history:
            if record.id == id:
                for key, value in kwargs.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
                if kwargs.get('status') == 'completed':
                    record.completed_at = datetime.now().isoformat()
                self.save_history()
                return record
        return None
    
    def get_record(self, id: str) -> Optional[DownloadRecord]:
        """获取单条记录"""
        for record in self.history:
            if record.id == id:
                return record
        return None
    
    def get_history(self, limit: int = 50, offset: int = 0) -> List[DownloadRecord]:
        """获取历史记录列表"""
        return self.history[offset:offset + limit]
    
    def clear_history(self, days: Optional[int] = None):
        """清理历史记录"""
        if days is None:
            self.history = []
        else:
            cutoff = datetime.now().timestamp() - (days * 86400)
            self.history = [
                record for record in self.history
                if datetime.fromisoformat(record.created_at).timestamp() > cutoff
            ]
        self.save_history()

# 创建全局历史记录管理器实例
history_manager = HistoryManager() 