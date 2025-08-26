"""
AI Prompt生成器路由模块
提供Web界面和API接口用于生成AI Prompt模板
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import os

from app.models import PromptRequest, PromptResponse
from app.services.prompt_service import PromptService
from app.dependencies import get_current_user

router = APIRouter(prefix="/prompt-generator", tags=["AI Prompt生成器"])


@router.get("/", response_class=HTMLResponse)
async def prompt_generator_page():
    """返回prompt生成器页面"""
    template_path = os.path.join("templates", "prompt_generator.html")
    if os.path.exists(template_path):
        return FileResponse(template_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <html>
            <head><title>文件未找到</title></head>
            <body>
                <h1>模板文件未找到</h1>
                <p>请确保 templates/prompt_generator.html 文件存在</p>
                <a href="/auth">返回登录页面</a>
            </body>
        </html>
        """, status_code=404)


@router.post("/generate", response_model=PromptResponse)
async def generate_prompt(
    prompt_data: PromptRequest,
    current_user: dict = Depends(get_current_user)
):
    """生成AI Prompt模板"""
    try:
        # 使用当前登录用户作为开发者
        developer = current_user['username']
        
        # 打印接收到的数据用于调试
        print(f"接收到的接口数量: {len(prompt_data.apis)}")
        for i, api in enumerate(prompt_data.apis, 1):
            print(f"接口{i}: {api.name}, DDL数量: {len(api.database_tables)}")
        
        generated_prompt = PromptService.generate_prompt_template(prompt_data, developer)
        
        return PromptResponse(
            success=True,
            prompt=generated_prompt
        )
    
    except Exception as e:
        print(f"生成prompt时出错: {str(e)}")
        return PromptResponse(
            success=False,
            error=f"生成prompt时出错: {str(e)}"
        )


@router.post("/generate-ai", response_model=PromptResponse)
async def generate_ai_prompt(
    prompt_data: PromptRequest,
    current_user: dict = Depends(get_current_user)
):
    """使用AI生成增强版Prompt模板"""
    try:
        # 首先生成基础prompt
        developer = current_user['username']
        base_prompt = PromptService.generate_prompt_template(prompt_data, developer)
        
        # 检查用户是否配置了AI服务
        from app.storage import get_storage
        storage = get_storage()
        ai_config = storage.get_user_ai_config_with_key(current_user['id'])
        
        if not ai_config or not all(field in ai_config and ai_config[field] 
                                   for field in ["api_type", "api_url", "api_key", "model_name"]):
            return PromptResponse(
                success=False,
                error="请先在个人中心配置AI服务"
            )
        
        # 提取prompt信息用于AI调用
        prompt_info = PromptService.extract_prompt_info_for_ai(prompt_data)
        
        # 填充AI请求模板
        ai_request_content = PromptService.fill_ai_request_template(prompt_info)
        
        # 使用AI处理响应参数表
        import httpx
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ai_config['api_key']}"
        }
        
        data = {
            "model": ai_config["model_name"],
            "messages": [{
                "role": "user", 
                "content": ai_request_content
            }],
            "max_tokens": 4000,
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(ai_config["api_url"], headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    ai_response = result["choices"][0].get("message", {}).get("content", "")
                    
                    # 记录AI聊天交互
                    PromptService.log_chat_interaction(
                        ai_request_content, 
                        ai_response, 
                        current_user.get('id')
                    )
                    
                    if ai_response:
                        # 将AI返回的响应参数表替换到原始prompt中
                        enhanced_prompt = PromptService.replace_response_table_in_prompt(
                            base_prompt, 
                            ai_response.strip()
                        )
                        
                        # 第二次AI调用：业务逻辑分析
                        try:
                            # 提取业务逻辑分析所需信息
                            business_info = PromptService.extract_business_logic_info_for_ai(enhanced_prompt)
                            
                            # 填充业务逻辑AI请求模板
                            business_ai_request_content = PromptService.fill_business_logic_ai_request_template(business_info)
                            
                            # 第二次AI调用
                            business_data = {
                                "model": ai_config["model_name"],
                                "messages": [{
                                    "role": "user", 
                                    "content": business_ai_request_content
                                }],
                                "max_tokens": 4000,
                                "temperature": 0.3
                            }
                            
                            async with httpx.AsyncClient(timeout=60.0) as business_client:
                                business_response = await business_client.post(ai_config["api_url"], headers=headers, json=business_data)
                                
                                if business_response.status_code == 200:
                                    business_result = business_response.json()
                                    if "choices" in business_result and len(business_result["choices"]) > 0:
                                        business_logic_response = business_result["choices"][0].get("message", {}).get("content", "")
                                        
                                        # 记录第二次AI聊天交互
                                        PromptService.log_chat_interaction(
                                            business_ai_request_content, 
                                            business_logic_response, 
                                            current_user.get('id')
                                        )
                                        
                                        if business_logic_response:
                                            # 将业务逻辑注入到prompt中
                                            final_prompt = PromptService.inject_business_logic_into_prompt(
                                                enhanced_prompt, 
                                                business_logic_response.strip()
                                            )
                                            
                                            return PromptResponse(
                                                success=True,
                                                prompt=final_prompt
                                            )
                                else:
                                    # 记录失败的第二次AI调用
                                    business_error_msg = f"业务逻辑AI调用失败，状态码: {business_response.status_code}"
                                    PromptService.log_chat_interaction(
                                        business_ai_request_content, 
                                        f"错误: {business_error_msg}", 
                                        current_user.get('id')
                                    )
                        
                        except Exception as business_e:
                            print(f"业务逻辑AI调用失败: {str(business_e)}")
                            # 第二次AI调用失败，但第一次成功，返回第一次的结果
                        
                        # 返回第一次AI增强的结果（如果第二次失败）
                        return PromptResponse(
                            success=True,
                            prompt=enhanced_prompt
                        )
            else:
                # 记录失败的AI调用
                error_msg = f"AI调用失败，状态码: {response.status_code}"
                PromptService.log_chat_interaction(
                    ai_request_content, 
                    f"错误: {error_msg}", 
                    current_user.get('id')
                )
        
        # AI调用失败，返回基础prompt
        return PromptResponse(
            success=True,
            prompt=base_prompt,
            error="AI增强失败，返回基础版本"
        )
    
    except Exception as e:
        print(f"生成AI prompt时出错: {str(e)}")
        # 失败时返回基础prompt
        try:
            developer = current_user['username']
            base_prompt = PromptService.generate_prompt_template(prompt_data, developer)
            return PromptResponse(
                success=True,
                prompt=base_prompt,
                error=f"AI生成失败，返回基础版本: {str(e)}"
            )
        except:
            return PromptResponse(
                success=False,
                error=f"生成prompt时出错: {str(e)}"
            )