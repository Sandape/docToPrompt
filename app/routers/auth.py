"""
用户认证路由模块 - JSON存储版本
提供用户注册、登录、密码管理等API接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
import os

from app.models import (
    UserCreate, UserLogin, UserUpdate, UserPasswordUpdate, 
    UserResponse, Token
)
from app.services.auth_service import AuthService
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["用户认证"])


@router.get("/test")
async def auth_test():
    """测试auth路由是否工作"""
    return {"message": "Auth router is working!"}


@router.get("/", response_class=HTMLResponse)
async def auth_page():
    """返回登录/注册页面"""
    template_path = os.path.join("templates", "auth.html")
    if os.path.exists(template_path):
        return FileResponse(template_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <html>
            <head><title>文件未找到</title></head>
            <body>
                <h1>认证页面未找到</h1>
                <p>请确保 templates/auth.html 文件存在</p>
            </body>
        </html>
        """, status_code=404)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    用户注册
    
    - **username**: 用户名（3-50字符）
    - **email**: 邮箱地址（用作登录账号）
    - **password**: 密码（6-50字符）
    """
    user = AuthService.register_user(user_data)
    
    # 移除敏感信息
    response_user = user.copy()
    response_user.pop('hashed_password', None)
    
    return UserResponse(**response_user)


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """
    用户登录
    
    - **email**: 邮箱地址
    - **password**: 密码
    """
    user = AuthService.authenticate_user(user_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = AuthService.create_user_token(user)
    return token


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    # 移除敏感信息
    response_user = current_user.copy()
    response_user.pop('hashed_password', None)
    
    return UserResponse(**response_user)


@router.put("/me", response_model=UserResponse)
async def update_user_info(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新当前用户信息
    
    - **username**: 新用户名（可选）
    """
    updated_user = AuthService.update_user_info(current_user['id'], user_update)
    
    # 移除敏感信息
    response_user = updated_user.copy()
    response_user.pop('hashed_password', None)
    
    return UserResponse(**response_user)


@router.put("/me/password")
async def update_password(
    password_update: UserPasswordUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    修改密码
    
    - **old_password**: 原密码
    - **new_password**: 新密码（6-50字符）
    """
    AuthService.update_user_password(current_user['id'], password_update)
    return {"message": "密码修改成功"}


@router.get("/profile", response_class=HTMLResponse)
async def profile_page():
    """返回个人中心页面"""
    template_path = os.path.join("templates", "profile.html")
    if os.path.exists(template_path):
        return FileResponse(template_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <html>
            <head><title>文件未找到</title></head>
            <body>
                <h1>个人中心页面未找到</h1>
                <p>请确保 templates/profile.html 文件存在</p>
            </body>
        </html>
        """, status_code=404)


@router.post("/logout")
async def logout():
    """
    用户登出
    
    注意：JWT是无状态的，客户端需要删除本地存储的令牌
    """
    return {"message": "登出成功，请删除本地存储的令牌"}