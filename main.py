from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime
import os
from dotenv import load_dotenv

# 导入应用模块
from app.models import HealthCheck, AppInfo
from app.routers import prompt_generator, auth, ai_simple, menu

# 加载环境变量
load_dotenv()

# 创建FastAPI应用实例
app = FastAPI(
    title="AI Prompt 生成器",
    description="一个专门用于生成AI Prompt模板的Web应用",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(menu.router)  # 主菜单路由，包含根路径
app.include_router(auth.router)
app.include_router(prompt_generator.router)
app.include_router(ai_simple.router)

# 基础路由已移至 menu.py

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """健康检查接口"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )

@app.get("/info", response_model=AppInfo)
async def app_info():
    """应用信息"""
    return AppInfo(
        name="AI Prompt生成器",
        version="1.0.0",
        description="一个专门用于生成AI Prompt模板的Web应用"
    )

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化存储"""
    # JSON存储会自动创建必要的文件和目录
    print("✅ JSON存储系统已初始化")
    
    # 打印所有路由用于调试
    print("\n📋 注册的路由:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"  {route.methods} {route.path}")
    print()

# 启动应用
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
