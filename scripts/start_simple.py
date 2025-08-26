#!/usr/bin/env python3
"""
简化版启动脚本 - 专注于快速启动服务器
"""

import uvicorn
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_banner():
    """打印启动横幅"""
    print("\n" + "="*80)
    print("🚀 AI Prompt Generator - 快速启动")
    print("="*80)

def print_routes():
    """打印主要路由信息"""
    try:
        from main import app
        
        print("\n📋 主要功能页面:")
        print(f"  🏠 主页: http://localhost:8080")
        print(f"  🔐 登录: http://localhost:8080/auth")
        print(f"  📝 Prompt生成: http://localhost:8080/prompt-generator")
        print(f"  👤 个人中心: http://localhost:8080/auth/profile")
        print(f"  📚 API文档: http://localhost:8080/docs")
        
        print(f"\n📊 总计接口数量: {len([r for r in app.routes if hasattr(r, 'path') and hasattr(r, 'methods')])}")
        
    except Exception as e:
        print(f"⚠ 无法获取路由信息: {e}")

def main():
    """主函数"""
    # 切换到项目根目录
    os.chdir(project_root)
    
    print_banner()
    print_routes()
    
    print("\n" + "="*80)
    print("🎉 启动服务器 (按 Ctrl+C 停止)")
    print("="*80)
    
    try:
        # 启动服务器
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8080,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n💡 建议:")
        print("1. 检查是否安装了所有依赖: pip install -r requirements.txt")
        print("2. 使用详细启动脚本: python scripts/start_server.py")
        sys.exit(1)

if __name__ == "__main__":
    main()

