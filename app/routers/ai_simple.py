"""
简化版AI配置路由模块
用于快速修复404问题
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import time
import httpx
from app.dependencies import get_current_user
from app.storage import get_storage

router = APIRouter(prefix="/ai", tags=["AI配置"])

# 简化的数据模型
class SimpleAIConfig(BaseModel):
    api_type: str
    api_url: str
    api_key: str
    model_name: str

class SimpleAITestRequest(BaseModel):
    message: str = "你好"

class SimpleAITestResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None
    test_message: Optional[str] = None
    ai_model: Optional[str] = None
    response_time: Optional[float] = None

@router.get("/config")
async def get_ai_config(current_user: dict = Depends(get_current_user)):
    """获取当前用户的AI配置信息（包含密钥）"""
    try:
        storage = get_storage()
        config = storage.get_user_ai_config_with_key(current_user['id'])
        
        if not config:
            return {
                "api_type": None,
                "api_url": None,
                "api_key": None,
                "model_name": None,
                "is_configured": False
            }
        
        return {
            "api_type": config.get("api_type"),
            "api_url": config.get("api_url"),
            "api_key": config.get("api_key"),
            "model_name": config.get("model_name"),
            "is_configured": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")

@router.put("/config")
async def update_ai_config(
    ai_config: SimpleAIConfig,
    current_user: dict = Depends(get_current_user)
):
    """更新AI配置"""
    try:
        storage = get_storage()
        config_dict = ai_config.dict()
        
        success = storage.update_user_ai_config(current_user['id'], config_dict)
        
        if not success:
            raise HTTPException(status_code=500, detail="AI配置更新失败")
        
        return {"message": "AI配置更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置更新失败: {str(e)}")

@router.post("/test", response_model=SimpleAITestResponse)
async def test_ai_connection(
    test_request: SimpleAITestRequest = SimpleAITestRequest(),
    current_user: dict = Depends(get_current_user)
):
    """测试AI连接"""
    start_time = time.time()
    
    try:
        storage = get_storage()
        config = storage.get_user_ai_config_with_key(current_user['id'])
        
        if not config:
            return SimpleAITestResponse(
                success=False,
                message="",
                error="未配置AI服务",
                test_message=test_request.message,
                ai_model=None,
                response_time=None
            )
        
        required_fields = ["api_type", "api_url", "api_key", "model_name"]
        if not all(field in config and config[field] for field in required_fields):
            return SimpleAITestResponse(
                success=False,
                message="",
                error="AI配置信息不完整",
                test_message=test_request.message,
                ai_model=config.get("model_name"),
                response_time=None
            )
        
        # 调用AI API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}"
        }
        
        data = {
            "model": config["model_name"],
            "messages": [{"role": "user", "content": test_request.message}],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(config["api_url"], headers=headers, json=data)
            
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("error", {}).get("message", error_detail)
                except:
                    pass
                
                return SimpleAITestResponse(
                    success=False,
                    message="",
                    error=f"API请求失败 (状态码: {response.status_code}): {error_detail}",
                    test_message=test_request.message,
                    ai_model=config["model_name"],
                    response_time=round(response_time, 2)
                )
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                if content:
                    return SimpleAITestResponse(
                        success=True,
                        message=content.strip(),
                        error=None,
                        test_message=test_request.message,
                        ai_model=config["model_name"],
                        response_time=round(response_time, 2)
                    )
                else:
                    return SimpleAITestResponse(
                        success=False,
                        message="",
                        error="AI响应内容为空",
                        test_message=test_request.message,
                        ai_model=config["model_name"],
                        response_time=round(response_time, 2)
                    )
            else:
                return SimpleAITestResponse(
                    success=False,
                    message="",
                    error="AI响应格式不正确",
                    test_message=test_request.message,
                    ai_model=config["model_name"],
                    response_time=round(response_time, 2)
                )
                
    except Exception as e:
        response_time = time.time() - start_time
        return SimpleAITestResponse(
            success=False,
            message="",
            error=f"AI服务连接失败: {str(e)}",
            test_message=test_request.message,
            ai_model=config.get("model_name") if 'config' in locals() else None,
            response_time=round(response_time, 2)
        )

@router.get("/default-config/{api_type}")
async def get_default_config(api_type: str):
    """获取默认配置"""
    if api_type not in ["openai", "deepseek"]:
        raise HTTPException(status_code=400, detail="不支持的API类型")
    
    default_configs = {
        "openai": {
            "api_url": "https://api.openai.com/v1/chat/completions",
            "model_name": "gpt-4o"
        },
        "deepseek": {
            "api_url": "https://api.deepseek.com/v1/chat/completions",
            "model_name": "deepseek-chat"
        }
    }
    
    return default_configs[api_type]
