#!/bin/bash

# AI Prompt Generator 启动脚本 (Unix/Linux/Mac)

# 设置UTF-8编码
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════════╗"
echo "║                           AI Prompt Generator 服务器                             ║"
echo "║                           一个专业的AI Prompt模板生成工具                        ║"
echo "╚══════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# 切换到项目根目录
cd "$PROJECT_ROOT"

echo "正在启动服务器..."
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "错误: 未找到Python解释器"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "使用Python: $PYTHON_CMD"

# 启动服务器
"$PYTHON_CMD" scripts/start_server.py

