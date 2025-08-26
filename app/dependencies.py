"""
依赖注入模块 - JSON存储版本
提供认证相关的依赖函数
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth_service import AuthService

# 安全方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    token = credentials.credentials
    token_data = AuthService.verify_token(token)
    
    if token_data is None:
        raise credentials_exception
    
    user = AuthService.get_user_by_id(token_data["user_id"])
    if user is None:
        raise credentials_exception
    
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    return user


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """获取当前活跃用户（别名函数，保持一致性）"""
    return current_user


# 可选的认证依赖，用于不强制要求登录的接口
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> dict | None:
    """获取当前用户（可选），如果未登录返回None"""
    if not credentials:
        return None
    
    token = credentials.credentials
    token_data = AuthService.verify_token(token)
    
    if token_data is None:
        return None
    
    user = AuthService.get_user_by_id(token_data["user_id"])
    if user is None or not user.get('is_active', True):
        return None
    
    return user