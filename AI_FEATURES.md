# AI集成功能说明

本项目已成功集成AI大模型功能，支持ChatGPT和DeepSeek等主流AI服务。

## 功能特性

### 1. AI配置管理
- **位置**: 个人中心 -> AI设置标签页
- **支持的AI服务**: OpenAI ChatGPT、DeepSeek
- **配置项**: API类型、API URL、API密钥、模型名称
- **安全性**: 密钥加密存储，界面不显示完整密钥

### 2. AI连接测试
- **功能**: 配置AI服务后可点击"测试连接"按钮
- **测试消息**: 发送"你好"给AI服务
- **反馈**: 显示连接是否成功及AI回复内容

### 3. AI增强Prompt生成
- **位置**: Prompt生成页面的"AI增强生成"按钮
- **功能**: 使用AI优化生成的Prompt模板
- **降级策略**: AI调用失败时返回基础版本

## 使用流程

### 步骤1: 配置AI服务
1. 登录系统后点击右上角"个人中心"
2. 切换到"AI设置"标签页
3. 选择API类型（OpenAI或DeepSeek）
4. 系统自动填充默认URL和模型名称
5. 输入您的API密钥
6. 点击"保存配置"

### 步骤2: 测试连接
1. 配置保存后点击"测试连接"
2. 系统会发送测试消息给AI服务
3. 查看测试结果，确认连接正常

### 步骤3: 使用AI增强功能
1. 在Prompt生成页面填写接口信息
2. 点击"AI增强生成"按钮（紫色）
3. 等待AI处理并生成优化后的Prompt

## 默认配置

### OpenAI
- **API URL**: https://api.openai.com/v1/chat/completions
- **默认模型**: gpt-4o

### DeepSeek
- **API URL**: https://api.deepseek.com/v1/chat/completions
- **默认模型**: deepseek-chat

## 错误处理

### 常见错误及解决方案

1. **"请先在个人中心配置AI服务"**
   - 需要先完成AI配置步骤

2. **"AI配置信息不完整"**
   - 检查是否填写了所有必需字段

3. **"API请求失败"**
   - 检查API密钥是否正确
   - 检查网络连接
   - 确认API服务可用

4. **"AI增强失败，返回基础版本"**
   - AI服务暂时不可用，但仍提供基础功能

## 技术实现

### 架构组件
- **数据模型**: `app/models.py` - AI配置相关模型
- **存储层**: `app/storage.py` - AI配置存储功能
- **服务层**: `app/services/ai_service.py` - AI调用逻辑
- **路由层**: `app/routers/ai.py` - AI配置API端点
- **前端**: `templates/profile.html` - AI设置界面

### API端点
- `GET /ai/config` - 获取AI配置
- `PUT /ai/config` - 更新AI配置
- `POST /ai/test` - 测试AI连接
- `POST /prompt-generator/generate-ai` - AI增强生成

### 安全特性
- API密钥加密存储
- 用户隔离的配置管理
- 安全的配置传输（不包含密钥）

## 验收标准确认

✅ **标准1**: 能够以和用户账号密码相同的方式存储大模型API配置信息
- 使用相同的JSON存储系统
- 配置信息与用户账户关联
- 支持配置的增删改查

✅ **标准2**: 配置大模型信息后，点击测试按钮，能够给大模型发送"你好"消息并反馈结果
- 实现了测试连接功能
- 发送固定测试消息"你好"
- 显示连接成功/失败状态和AI回复

✅ **标准3**: 兼容ChatGPT4o和DeepSeekV3
- 支持OpenAI API格式（ChatGPT4o）
- 支持DeepSeek API格式
- 提供默认配置模板
- 统一的API调用接口

## 后续扩展

可以轻松扩展支持更多AI服务：
1. 在`AIService.DEFAULT_MODELS`中添加新的配置
2. 在模型验证中添加新的API类型
3. 如需要，调整API调用格式
