"""
用户认证服务模块 - JSON存储版本
负责处理用户注册、登录、密码管理等认证相关业务逻辑
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv

from app.storage import get_storage
from app.models import UserCreate, UserLogin, UserPasswordUpdate, UserUpdate, Token

# 加载环境变量
load_dotenv()

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """认证服务类"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希值"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            if email is None or user_id is None:
                return None
            return {"email": email, "user_id": user_id}
        except JWTError:
            return None
    
    @classmethod
    def register_user(cls, user_data: UserCreate) -> dict:
        """用户注册"""
        try:
            # 加密密码
            hashed_password = cls.get_password_hash(user_data.password)
            
            # 创建用户
            storage = get_storage()
            user = storage.create_user(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password
            )
            
            return user
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    @classmethod
    def authenticate_user(cls, user_data: UserLogin) -> Optional[dict]:
        """用户登录认证"""
        storage = get_storage()
        user = storage.get_user_by_email(user_data.email)
        if not user:
            return None
        if not cls.verify_password(user_data.password, user['hashed_password']):
            return None
        if not user.get('is_active', True):
            return None
        return user
    
    @classmethod
    def create_user_token(cls, user: dict) -> Token:
        """创建用户令牌"""
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = cls.create_access_token(
            data={"sub": user['email'], "user_id": user['id']},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[dict]:
        """根据邮箱获取用户"""
        storage = get_storage()
        return storage.get_user_by_email(email)
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[dict]:
        """根据用户名获取用户"""
        storage = get_storage()
        return storage.get_user_by_username(username)
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[dict]:
        """根据ID获取用户"""
        storage = get_storage()
        return storage.get_user_by_id(user_id)
    
    @classmethod
    def update_user_info(cls, user_id: int, user_update: UserUpdate) -> dict:
        """更新用户信息"""
        user = cls.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 准备更新数据
        updates = {}
        if user_update.username is not None:
            updates['username'] = user_update.username
        
        try:
            storage = get_storage()
            updated_user = storage.update_user(user_id, updates)
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            return updated_user
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    @classmethod
    def update_user_password(cls, user_id: int, password_update: UserPasswordUpdate) -> dict:
        """更新用户密码"""
        user = cls.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证原密码
        if not cls.verify_password(password_update.old_password, user['hashed_password']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="原密码错误"
            )
        
        # 更新密码
        new_hashed_password = cls.get_password_hash(password_update.new_password)
        updates = {'hashed_password': new_hashed_password}
        
        storage = get_storage()
        updated_user = storage.update_user(user_id, updates)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return updated_user