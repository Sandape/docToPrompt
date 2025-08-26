# 启动脚本使用说明

本目录包含AI Prompt Generator项目的启动脚本，提供完整的日志输出和系统信息。

## 文件说明

- `start_server.py` - 完整功能启动脚本（包含系统检查、依赖验证等）
- `start_simple.py` - 简化启动脚本（快速启动，最少检查）
- `start_server.bat` - Windows批处理脚本
- `start_server.sh` - Unix/Linux/Mac shell脚本

## 功能特性

✅ 完整的系统信息检查  
✅ 依赖包状态验证  
✅ 环境配置检查  
✅ 详细的路由信息打印  
✅ 完整的日志记录  
✅ 优雅的错误处理  

## 使用方法

### 推荐方式（快速启动）

如果遇到依赖检查问题，推荐使用简化版：

```cmd
# Windows
python scripts\start_simple.py

# Unix/Linux/Mac  
python3 scripts/start_simple.py
```

### 完整功能启动

### Windows用户
```cmd
# 方法1: 直接运行批处理文件
scripts\start_server.bat

# 方法2: 运行Python脚本
python scripts\start_server.py
```

### Unix/Linux/Mac用户
```bash
# 方法1: 运行shell脚本
./scripts/start_server.sh

# 方法2: 运行Python脚本
python3 scripts/start_server.py
```

## 服务器信息

- **端口**: 8080
- **主页**: http://localhost:8080
- **API文档**: http://localhost:8080/docs
- **ReDoc文档**: http://localhost:8080/redoc

## 日志文件

启动脚本会在 `logs/` 目录下生成详细的日志文件，文件名格式为：
`server_YYYYMMDD_HHMMSS.log`

## 停止服务器

按 `Ctrl+C` 停止服务器
