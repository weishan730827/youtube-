import logging
from typing import List, Dict
from queue_manager import queue_manager
from history_manager import history_manager
import uuid

logger = logging.getLogger(__name__)

class BatchManager:
    def __init__(self):
        self.batch_tasks: Dict[str, Dict] = {}
    
    def create_batch(self, urls: List[str], options: Dict = None) -> str:
        """创建批量下载任务"""
        batch_id = str(uuid.uuid4())
        tasks = []
        
        for url in urls:
            task_id = str(uuid.uuid4())
            task = {
                'task_id': task_id,
                'url': url,
                'status': 'pending',
                'options': options or {}
            }
            tasks.append(task)
            
            # 添加到下载队列
            queue_manager.add_task(task_id, url, options=options)
        
        self.batch_tasks[batch_id] = {
            'tasks': tasks,
            'total': len(tasks),
            'completed': 0,
            'failed': 0
        }
        
        return batch_id
    
    def get_batch_status(self, batch_id: str) -> Dict:
        """获取批���任务状态"""
        if batch_id not in self.batch_tasks:
            return None
            
        batch = self.batch_tasks[batch_id]
        completed = 0
        failed = 0
        
        for task in batch['tasks']:
            status = history_manager.get_record(task['task_id'])
            if status:
                if status.status == 'completed':
                    completed += 1
                elif status.status == 'error':
                    failed += 1
        
        batch['completed'] = completed
        batch['failed'] = failed
        
        return {
            'total': batch['total'],
            'completed': completed,
            'failed': failed,
            'progress': (completed + failed) / batch['total'] * 100,
            'tasks': [
                {
                    'task_id': task['task_id'],
                    'url': task['url'],
                    'status': history_manager.get_record(task['task_id']).status if history_manager.get_record(task['task_id']) else 'pending'
                }
                for task in batch['tasks']
            ]
        }

# 创建全局批量下载管理器实例
batch_manager = BatchManager() 