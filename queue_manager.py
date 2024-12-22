import queue
import threading
import logging
import time
from typing import Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from download_manager import download_manager

logger = logging.getLogger(__name__)

@dataclass
class DownloadTask:
    task_id: str
    url: str
    created_at: datetime
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3

class QueueManager:
    def __init__(self, max_concurrent: int = 2):
        self.task_queue = queue.PriorityQueue()
        self.max_concurrent = max_concurrent
        self.current_downloads = 0
        self.lock = threading.Lock()
        self.running = True
        
        # 启动处理线程
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.daemon = True
        self.worker_thread.start()
    
    def add_task(self, task_id: str, url: str, priority: int = 0) -> bool:
        """添加下载任务到队列"""
        try:
            task = DownloadTask(
                task_id=task_id,
                url=url,
                created_at=datetime.now(),
                priority=priority
            )
            self.task_queue.put((priority, task))
            logger.info(f"任务 {task_id} 已添加到队列")
            return True
        except Exception as e:
            logger.error(f"添加任务到队列失败: {str(e)}")
            return False
    
    def _process_queue(self):
        """处理队列中的任务"""
        while self.running:
            try:
                if self.current_downloads >= self.max_concurrent:
                    time.sleep(1)
                    continue
                    
                try:
                    _, task = self.task_queue.get_nowait()
                except queue.Empty:
                    time.sleep(1)
                    continue
                
                with self.lock:
                    self.current_downloads += 1
                
                # 启动新线程处理下载
                thread = threading.Thread(
                    target=self._handle_download,
                    args=(task,)
                )
                thread.daemon = True
                thread.start()
                
            except Exception as e:
                logger.error(f"处理队列任务失败: {str(e)}")
                time.sleep(1)
    
    def _handle_download(self, task: DownloadTask):
        """处理单个下载任务"""
        try:
            # 更新任务状态为下载中
            download_manager.update_status(
                task.task_id,
                status='downloading',
                progress=0
            )
            
            # TODO: 实际的下载处理逻辑
            # 这部分需要和 VideoDownloader 类整合
            
        except Exception as e:
            logger.error(f"下载任务 {task.task_id} 失败: {str(e)}")
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                self.task_queue.put((task.priority, task))
                logger.info(f"任务 {task.task_id} 将重试 ({task.retry_count}/{task.max_retries})")
            else:
                download_manager.update_status(
                    task.task_id,
                    status='error',
                    error_message=str(e)
                )
        finally:
            with self.lock:
                self.current_downloads -= 1
    
    def stop(self):
        """停止队列处理"""
        self.running = False
        self.worker_thread.join()
        logger.info("下载队列管理器已停止")

# 创建全局队列管理器实例
queue_manager = QueueManager() 