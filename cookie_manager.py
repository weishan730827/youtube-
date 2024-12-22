import browser_cookie3
import logging
from pathlib import Path
from typing import Dict
import os
import time

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CookieManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.cookie_file = self.base_dir / 'cookies.txt'
        self.domains = ['youtube.com', '.youtube.com']
        logger.info(f"CookieManager初始化，基础目录: {self.base_dir}")
        
    def get_cookies(self) -> Dict:
        """获取所有可用的cookies"""
        cookies = {}
        
        # 1. 尝试从浏览器获取
        browser_cookies = self._get_browser_cookies()
        if browser_cookies:
            cookies.update(browser_cookies)
            logger.info(f"成功从浏览器获取cookies: {len(browser_cookies)}个")
            
        # 2. 尝试从文件获取
        file_cookies = self._get_cookies_from_file()
        if file_cookies:
            cookies.update(file_cookies)
            logger.info(f"成功从文件获取cookies: {len(file_cookies)}个")
            
        if not cookies:
            logger.warning("未能获取到任何cookies")
            
        return cookies
    
    def _get_browser_cookies(self) -> Dict:
        """从浏览器获取cookies"""
        cookies = {}
        browsers = [
            ('chrome', browser_cookie3.chrome),
            ('firefox', browser_cookie3.firefox),
            ('edge', browser_cookie3.edge),
            ('safari', browser_cookie3.safari),
        ]
        
        for browser_name, browser_func in browsers:
            try:
                logger.debug(f"尝试从{browser_name}获取cookies...")
                cj = browser_func(domain_name='youtube.com')
                for cookie in cj:
                    if cookie.domain in self.domains:
                        cookies[cookie.name] = cookie.value
                logger.info(f"从 {browser_name} 获取到 {len(cookies)} 个cookies")
                if cookies:
                    break
            except Exception as e:
                logger.debug(f"从 {browser_name} 获取cookies失败: {str(e)}")
                
        return cookies
        
    def _get_cookies_from_file(self) -> Dict:
        """从文件获取cookies"""
        cookies = {}
        try:
            if not self.cookie_file.exists():
                logger.warning(f"cookies文件不存在: {self.cookie_file}")
                return cookies
                
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    try:
                        domain, _, _, _, expiry, name, value = line.strip().split('\t')
                        if any(d in domain for d in self.domains):
                            cookies[name] = value
                    except Exception as e:
                        logger.debug(f"解析cookies行失败: {str(e)}")
                        
            logger.info(f"从文件读取到 {len(cookies)} 个cookies")
            
        except Exception as e:
            logger.error(f"读取cookies文件失败: {str(e)}")
            
        return cookies

    def save_cookies(self, cookies: Dict) -> bool:
        """保存cookies到文件"""
        try:
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                for name, value in cookies.items():
                    f.write(f".youtube.com\tTRUE\t/\tFALSE\t{int(time.time()) + 3600*24*365}\t{name}\t{value}\n")
            logger.info(f"成功保存 {len(cookies)} 个cookies到文件")
            return True
        except Exception as e:
            logger.error(f"保存cookies失败: {str(e)}")
            return False 