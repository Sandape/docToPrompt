"""
菜单页面路由模块
提供主菜单、批量转译、接口类型选择等页面的路由
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse
import os

router = APIRouter(tags=["菜单页面"])


@router.get("/", response_class=HTMLResponse)
async def main_menu():
    """主菜单页面"""
    template_path = os.path.join("templates", "main_menu.html")
    if os.path.exists(template_path):
        return FileResponse(template_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <html>
            <head><title>文件未找到</title></head>
            <body>
                <h1>主菜单模板文件未找到</h1>
                <p>请确保 templates/main_menu.html 文件存在</p>
                <a href="/auth">返回登录页面</a>
            </body>
        </html>
        """, status_code=404)


@router.get("/batch-translation", response_class=HTMLResponse)
async def batch_translation_page():
    """批量转译页面"""
    template_path = os.path.join("templates", "batch_translation.html")
    if os.path.exists(template_path):
        return FileResponse(template_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <html>
            <head><title>文件未找到</title></head>
            <body>
                <h1>批量转译模板文件未找到</h1>
                <p>请确保 templates/batch_translation.html 文件存在</p>
                <a href="/">返回主菜单</a>
            </body>
        </html>
        """, status_code=404)


@router.get("/interface-type-menu", response_class=HTMLResponse)
async def interface_type_menu_page():
    """接口类型选择菜单页面"""
    template_path = os.path.join("templates", "interface_type_menu.html")
    if os.path.exists(template_path):
        return FileResponse(template_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <html>
            <head><title>文件未找到</title></head>
            <body>
                <h1>接口类型菜单模板文件未找到</h1>
                <p>请确保 templates/interface_type_menu.html 文件存在</p>
                <a href="/">返回主菜单</a>
            </body>
        </html>
        """, status_code=404)
