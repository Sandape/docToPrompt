#!/usr/bin/env python3
"""
AI Prompt Generator 启动脚本
提供完整的日志输出和接口信息
"""

import uvicorn
import sys
import os
import time
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置完整的日志配置
def setup_logging():
    """配置详细的日志输出"""
    # 创建日志目录
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    log_format = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    
    # 配置root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                log_dir / f"server_{time.strftime('%Y%m%d_%H%M%S')}.log",
                encoding='utf-8'
            )
        ]
    )
    
    # 设置各个模块的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    return logging.getLogger(__name__)

def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════════╗
║                           AI Prompt Generator 服务器                             ║
║                           一个专业的AI Prompt模板生成工具                        ║
╚══════════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_system_info(logger):
    """打印系统信息"""
    import platform
    import psutil
    
    logger.info("="*80)
    logger.info("系统信息:")
    logger.info(f"  操作系统: {platform.system()} {platform.release()}")
    logger.info(f"  Python版本: {platform.python_version()}")
    logger.info(f"  CPU核心数: {psutil.cpu_count()}")
    logger.info(f"  内存总量: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    logger.info(f"  项目根目录: {project_root}")
    logger.info("="*80)

def check_dependencies(logger):
    """检查依赖包"""
    logger.info("检查依赖包...")
    
    # 包名映射：安装名 -> 导入名
    required_packages = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn", 
        "pydantic": "pydantic",
        "python-jose": "jose",
        "passlib": "passlib",
        "python-dotenv": "dotenv",
        "httpx": "httpx",
        "jinja2": "jinja2",
        "psutil": "psutil"
    }
    
    missing_packages = []
    
    for install_name, import_name in required_packages.items():
        try:
            # 尝试导入包
            module = __import__(import_name)
            # 对于某些包，验证具体的子模块
            if import_name == "jose":
                from jose import jwt  # 验证JWT功能
            elif import_name == "passlib":
                from passlib.context import CryptContext  # 验证加密功能
            elif import_name == "uvicorn":
                import uvicorn.main  # 验证主模块
            
            logger.info(f"  ✓ {install_name}")
        except ImportError as e:
            logger.error(f"  ✗ {install_name} - 未安装或导入失败: {str(e)}")
            missing_packages.append(install_name)
        except Exception as e:
            logger.warning(f"  ⚠ {install_name} - 已安装但可能有问题: {str(e)}")
    
    if missing_packages:
        logger.error(f"缺少依赖包: {', '.join(missing_packages)}")
        logger.error("请运行: pip install -r requirements.txt")
        return False
    
    logger.info("所有依赖包检查完成 ✓")
    return True

def check_environment(logger):
    """检查环境配置"""
    logger.info("检查环境配置...")
    
    # 检查必要的目录
    required_dirs = ["app", "templates", "data"]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            logger.info(f"  ✓ {dir_name}/ 目录存在")
        else:
            logger.warning(f"  ⚠ {dir_name}/ 目录不存在")
    
    # 检查模板文件
    template_files = ["auth.html", "profile.html", "prompt_generator.html"]
    for template in template_files:
        template_path = project_root / "templates" / template
        if template_path.exists():
            logger.info(f"  ✓ 模板文件 {template} 存在")
        else:
            logger.warning(f"  ⚠ 模板文件 {template} 不存在")
    
    # 检查数据文件
    data_file = project_root / "data" / "users.json"
    if data_file.exists():
        logger.info(f"  ✓ 数据文件 users.json 存在")
    else:
        logger.info(f"  ⚠ 数据文件 users.json 不存在，将自动创建")
    
    logger.info("环境配置检查完成 ✓")

def print_route_info(logger):
    """打印路由信息"""
    try:
        from main import app
        
        logger.info("="*80)
        logger.info("已注册的API接口:")
        logger.info("="*80)
        
        # 按路径分组整理路由
        routes_by_prefix = {}
        
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = list(route.methods)
                if 'OPTIONS' in methods:
                    methods.remove('OPTIONS')
                
                if methods:  # 只显示有实际HTTP方法的路由
                    # 确定路由分组
                    path = route.path
                    if path.startswith('/auth'):
                        prefix = '🔐 用户认证'
                    elif path.startswith('/ai'):
                        prefix = '🤖 AI配置'
                    elif path.startswith('/prompt-generator'):
                        prefix = '📝 Prompt生成'
                    elif path in ['/', '/health', '/info']:
                        prefix = '🏠 基础接口'
                    else:
                        prefix = '🔧 其他接口'
                    
                    if prefix not in routes_by_prefix:
                        routes_by_prefix[prefix] = []
                    
                    routes_by_prefix[prefix].append({
                        'methods': methods,
                        'path': path,
                        'name': getattr(route, 'name', ''),
                        'summary': getattr(route, 'summary', '')
                    })
        
        # 打印分组的路由信息
        for prefix, routes in routes_by_prefix.items():
            logger.info(f"\n{prefix}:")
            for route in sorted(routes, key=lambda x: x['path']):
                methods_str = ', '.join(sorted(route['methods']))
                logger.info(f"  [{methods_str:12}] {route['path']}")
        
        logger.info("\n" + "="*80)
        logger.info(f"总计: {sum(len(routes) for routes in routes_by_prefix.values())} 个接口")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"获取路由信息失败: {e}")

def print_startup_success(logger, host, port):
    """打印启动成功信息"""
    logger.info("="*80)
    logger.info("🎉 服务器启动成功!")
    logger.info("="*80)
    logger.info(f"🌐 服务地址: http://localhost:{port}")
    logger.info(f"📚 API文档: http://localhost:{port}/docs")
    logger.info(f"📖 ReDoc文档: http://localhost:{port}/redoc")
    logger.info("="*80)
    logger.info("💡 快速访问:")
    logger.info(f"   登录页面: http://localhost:{port}/auth")
    logger.info(f"   主功能页: http://localhost:{port}/prompt-generator")
    logger.info(f"   个人中心: http://localhost:{port}/auth/profile")
    logger.info(f"   健康检查: http://localhost:{port}/health")
    logger.info("="*80)
    logger.info("按 Ctrl+C 停止服务器")
    logger.info("="*80)

def main():
    """主函数"""
    # 设置配置
    HOST = "0.0.0.0"
    PORT = 8080
    RELOAD = True
    LOG_LEVEL = "info"
    
    # 初始化日志
    logger = setup_logging()
    
    try:
        # 打印启动横幅
        print_banner()
        
        # 系统信息检查
        print_system_info(logger)
        
        # 依赖检查
        if not check_dependencies(logger):
            sys.exit(1)
        
        # 环境检查
        check_environment(logger)
        
        # 打印路由信息
        print_route_info(logger)
        
        # 打印启动成功信息
        print_startup_success(logger, HOST, PORT)
        
        # 启动服务器
        uvicorn.run(
            "main:app",
            host=HOST,
            port=PORT,
            reload=RELOAD,
            log_level=LOG_LEVEL,
            access_log=True,
            reload_dirs=[str(project_root)],
            reload_excludes=["logs/*", "data/*", "__pycache__"]
        )
        
    except KeyboardInterrupt:
        logger.info("\n👋 服务器已停止")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
