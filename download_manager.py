import time
from threading import Lock
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DownloadStatus:
    task_id: str
    url: str
    status: str  # 'pending', 'downloading', 'completed', 'error'
    progress: float
    speed: str
    eta: str
    filename: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

class DownloadManager:
    def __init__(self):
        self._tasks: Dict[str, DownloadStatus] = {}
        self._lock = Lock()

    def create_task(self, task_id: str, url: str) -> DownloadStatus:
        """创建新的下载任务"""
        with self._lock:
            status = DownloadStatus(
                task_id=task_id,
                url=url,
                status='pending',
                progress=0.0,
                speed='0 KB/s',
                eta='未知',
                filename=None,
                error_message=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self._tasks[task_id] = status
            return status

    def update_status(self, task_id: str, **kwargs) -> Optional[DownloadStatus]:
        """更新任务状态"""
        with self._lock:
            if task_id not in self._tasks:
                return None
            
            status = self._tasks[task_id]
            for key, value in kwargs.items():
                if hasattr(status, key):
                    setattr(status, key, value)
            status.updated_at = datetime.now()
            return status

    def get_status(self, task_id: str) -> Optional[DownloadStatus]:
        """获取任务状态"""
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks(self, limit: int = 100) -> list:
        """获取任务列表"""
        with self._lock:
            return list(sorted(
                self._tasks.values(),
                key=lambda x: x.created_at,
                reverse=True
            ))[:limit]

    def clean_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        now = datetime.now()
        with self._lock:
            for task_id, status in list(self._tasks.items()):
                age = (now - status.created_at).total_seconds() / 3600
                if age > max_age_hours:
                    del self._tasks[task_id]

# 创建全局下载���理器实例
download_manager = DownloadManager() 