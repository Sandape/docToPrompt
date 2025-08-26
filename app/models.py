from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


# 接口信息模型
class ApiInfo(BaseModel):
    """单个接口信息模型"""
    name: str = Field(..., min_length=1, max_length=100, description="接口名称")
    route: str = Field(..., min_length=1, max_length=200, description="接口路由")
    request_example: str = Field(..., description="请求报文示例")
    response_example: str = Field(..., description="响应报文示例")
    database_tables: List[str] = Field(default_factory=list, description="关联数据库表DDL列表")


class PromptRequest(BaseModel):
    """Prompt生成请求模型"""
    apis: List[ApiInfo] = Field(..., min_items=1, description="接口信息列表")


class PromptResponse(BaseModel):
    """Prompt生成响应模型"""
    success: bool = Field(description="是否成功")
    prompt: Optional[str] = Field(None, description="生成的prompt内容")
    error: Optional[str] = Field(None, description="错误信息")


class FieldInfo(BaseModel):
    """字段信息模型"""
    name: str = Field(description="字段名称")
    type: str = Field(description="字段类型")
    required: str = Field(description="是否必填")
    description: str = Field(description="字段描述")


class HealthCheck(BaseModel):
    """健康检查模型"""
    status: str = Field(description="服务状态")
    timestamp: str = Field(description="检查时间")


class AppInfo(BaseModel):
    """应用信息模型"""
    name: str = Field(description="应用名称")
    version: str = Field(description="应用版本")
    description: str = Field(description="应用描述")


# ============ 用户认证相关模型 ============

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")


class UserCreate(UserBase):
    """用户注册模型"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserLogin(BaseModel):
    """用户登录模型"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户信息更新模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")


class UserPasswordUpdate(BaseModel):
    """用户密码更新模型"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT令牌模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """令牌数据模型"""
    email: Optional[str] = None
    user_id: Optional[int] = None


# ============ AI配置相关模型 ============

class AIConfig(BaseModel):
    """AI配置模型"""
    api_type: str = Field(..., description="API类型", pattern="^(openai|deepseek)$")
    api_url: str = Field(..., description="API URL地址")
    api_key: str = Field(..., description="API密钥")
    model_name: str = Field(..., description="模型名称")


class AIConfigUpdate(BaseModel):
    """AI配置更新模型"""
    api_type: Optional[str] = Field(None, description="API类型", pattern="^(openai|deepseek)$")
    api_url: Optional[str] = Field(None, description="API URL地址")
    api_key: Optional[str] = Field(None, description="API密钥")
    model_name: Optional[str] = Field(None, description="模型名称")


class AIConfigResponse(BaseModel):
    """AI配置响应模型（不包含密钥）"""
    api_type: Optional[str] = None
    api_url: Optional[str] = None
    model_name: Optional[str] = None
    is_configured: bool = False


class AITestRequest(BaseModel):
    """AI测试请求模型"""
    message: str = Field(default="你好", description="测试消息")


class AITestResponse(BaseModel):
    """AI测试响应模型"""
    success: bool = Field(description="测试是否成功")
    message: str = Field(description="AI完整响应内容")
    error: Optional[str] = Field(None, description="错误信息")
    test_message: Optional[str] = Field(None, description="发送的测试消息")
    ai_model: Optional[str] = Field(None, description="使用的AI模型")
    response_time: Optional[float] = Field(None, description="响应时间（秒）")