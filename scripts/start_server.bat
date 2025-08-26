@echo off
chcp 65001 >nul
title AI Prompt Generator Server

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════════╗
echo ║                           AI Prompt Generator 服务器                             ║
echo ║                           一个专业的AI Prompt模板生成工具                        ║
echo ╚══════════════════════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0.."

echo 正在启动服务器...
echo.

python scripts\start_server.py

pause

