"""
简单的JSON文件存储系统
用于存储用户数据，适合个人使用
"""

import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path


class JSONStorage:
    """JSON文件存储管理器"""
    
    def __init__(self, storage_dir: str = "data"):
        """
        初始化存储管理器
        
        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.users_file = self.storage_dir / "users.json"
        
        # 确保用户文件存在
        if not self.users_file.exists():
            self._save_users([])
    
    def _load_users(self) -> List[Dict[str, Any]]:
        """加载用户数据"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_users(self, users: List[Dict[str, Any]]) -> None:
        """保存用户数据"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2, default=str)
    
    def get_next_user_id(self) -> int:
        """获取下一个用户ID"""
        users = self._load_users()
        if not users:
            return 1
        return max(user.get('id', 0) for user in users) + 1
    
    def create_user(self, username: str, email: str, hashed_password: str) -> Dict[str, Any]:
        """
        创建新用户
        
        Args:
            username: 用户名
            email: 邮箱
            hashed_password: 加密后的密码
            
        Returns:
            创建的用户数据
        """
        users = self._load_users()
        
        # 检查邮箱是否已存在
        if any(user['email'] == email for user in users):
            raise ValueError("邮箱地址已被注册")
        
        # 检查用户名是否已存在
        if any(user['username'] == username for user in users):
            raise ValueError("用户名已被使用")
        
        # 创建新用户
        new_user = {
            'id': self.get_next_user_id(),
            'username': username,
            'email': email,
            'hashed_password': hashed_password,
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': None
        }
        
        users.append(new_user)
        self._save_users(users)
        
        return new_user
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        users = self._load_users()
        return next((user for user in users if user['email'] == email), None)
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        users = self._load_users()
        return next((user for user in users if user['username'] == username), None)
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        users = self._load_users()
        return next((user for user in users if user['id'] == user_id), None)
    
    def update_user(self, user_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            updates: 要更新的字段
            
        Returns:
            更新后的用户数据
        """
        users = self._load_users()
        
        for i, user in enumerate(users):
            if user['id'] == user_id:
                # 检查用户名是否重复
                if 'username' in updates and updates['username'] != user['username']:
                    if any(u['username'] == updates['username'] for u in users if u['id'] != user_id):
                        raise ValueError("用户名已被使用")
                
                # 更新字段
                user.update(updates)
                user['updated_at'] = datetime.now().isoformat()
                users[i] = user
                
                self._save_users(users)
                return user
        
        return None
    
    def delete_user(self, user_id: int) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        users = self._load_users()
        original_count = len(users)
        
        users = [user for user in users if user['id'] != user_id]
        
        if len(users) < original_count:
            self._save_users(users)
            return True
        
        return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户（不包含密码）"""
        users = self._load_users()
        # 移除密码字段
        safe_users = []
        for user in users:
            safe_user = user.copy()
            safe_user.pop('hashed_password', None)
            safe_users.append(safe_user)
        return safe_users
    
    def update_user_ai_config(self, user_id: int, ai_config: Dict[str, Any]) -> bool:
        """
        更新用户的AI配置
        
        Args:
            user_id: 用户ID
            ai_config: AI配置信息
            
        Returns:
            是否更新成功
        """
        users = self._load_users()
        
        for i, user in enumerate(users):
            if user['id'] == user_id:
                if 'ai_config' not in user:
                    user['ai_config'] = {}
                
                # 更新AI配置
                user['ai_config'].update(ai_config)
                user['updated_at'] = datetime.now().isoformat()
                users[i] = user
                
                self._save_users(users)
                return True
        
        return False
    
    def get_user_ai_config(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        获取用户的AI配置
        
        Args:
            user_id: 用户ID
            
        Returns:
            AI配置信息（不包含密钥）
        """
        users = self._load_users()
        
        for user in users:
            if user['id'] == user_id:
                ai_config = user.get('ai_config', {})
                if ai_config:
                    # 返回安全的配置信息（不包含密钥）
                    safe_config = ai_config.copy()
                    safe_config.pop('api_key', None)
                    return safe_config
                return {}
        
        return None
    
    def get_user_ai_config_with_key(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        获取用户的完整AI配置（包含密钥，仅用于内部调用）
        
        Args:
            user_id: 用户ID
            
        Returns:
            完整的AI配置信息
        """
        users = self._load_users()
        
        for user in users:
            if user['id'] == user_id:
                return user.get('ai_config', {})
        
        return None


# 延迟初始化的全局存储实例
_storage_instance = None

def get_storage() -> JSONStorage:
    """获取存储实例（单例模式）"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = JSONStorage()
    return _storage_instance
