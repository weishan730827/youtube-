import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.users_file = self.base_dir / 'users.json'
        self.secret_key = 'your-secret-key'  # 建议使用环境变量存储
        self.token_expire_days = 7
        self.users: Dict[str, Dict] = {}
        self.load_users()
    
    def load_users(self):
        """从文件加载用户数据"""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
                logger.info(f"已加载 {len(self.users)} 个用户")
        except Exception as e:
            logger.error(f"加载用户数据失败: {str(e)}")
            self.users = {}
    
    def save_users(self):
        """保存用户数据到文件"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=4)
            logger.info("用户数据已保存")
        except Exception as e:
            logger.error(f"保存用户数据失败: {str(e)}")
    
    def create_user(self, username: str, password: str, is_admin: bool = False) -> bool:
        """创建新用户"""
        if username in self.users:
            return False
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        
        self.users[username] = {
            'password': hashed.decode(),
            'is_admin': is_admin,
            'created_at': datetime.now().isoformat()
        }
        
        self.save_users()
        return True
    
    def verify_user(self, username: str, password: str) -> bool:
        """验证用户密码"""
        if username not in self.users:
            return False
        
        stored_hash = self.users[username]['password'].encode()
        return bcrypt.checkpw(password.encode(), stored_hash)
    
    def generate_token(self, username: str) -> str:
        """生成JWT令牌"""
        payload = {
            'username': username,
            'is_admin': self.users[username]['is_admin'],
            'exp': datetime.utcnow() + timedelta(days=self.token_expire_days)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            if payload['username'] not in self.users:
                return None
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            return None
        except jwt.InvalidTokenError:
            logger.warning("无效的令牌")
            return None

# 创建全局认证管理器实例
auth_manager = AuthManager()

# 创建装饰器用于保护API端点
def require_auth(func):
    def wrapper(self, *args, **kwargs):
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            self.send_error(401, 'Unauthorized')
            return
        
        token = auth_header.split(' ')[1]
        user = auth_manager.verify_token(token)
        if not user:
            self.send_error(401, 'Unauthorized')
            return
        
        self.user = user
        return func(self, *args, **kwargs)
    return wrapper

def require_admin(func):
    def wrapper(self, *args, **kwargs):
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            self.send_error(401, 'Unauthorized')
            return
        
        token = auth_header.split(' ')[1]
        user = auth_manager.verify_token(token)
        if not user or not user.get('is_admin'):
            self.send_error(403, 'Forbidden')
            return
        
        self.user = user
        return func(self, *args, **kwargs)
    return wrapper 