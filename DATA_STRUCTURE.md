# 数据结构说明

## JSON文件存储

本应用使用简单的JSON文件来存储用户数据，适合个人使用。

### 存储位置

- 默认存储目录: `data/`
- 用户数据文件: `data/users.json`

### 用户数据结构

```json
[
  {
    "id": 1,
    "username": "demo_user",
    "email": "demo@example.com",
    "hashed_password": "$2b$12$...",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00.123456",
    "updated_at": "2024-01-15T11:00:00.123456"
  }
]
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 用户唯一标识符，自动递增 |
| `username` | string | 用户名，3-50字符，唯一 |
| `email` | string | 邮箱地址，用作登录账号，唯一 |
| `hashed_password` | string | bcrypt加密后的密码 |
| `is_active` | boolean | 用户是否活跃，默认true |
| `created_at` | string | 创建时间，ISO格式 |
| `updated_at` | string | 最后更新时间，ISO格式 |

## 数据操作

### 自动创建

- 首次启动时自动创建`data`目录和`users.json`文件
- 如果文件损坏，会自动重新创建空文件

### 数据安全

- 密码使用bcrypt算法加密存储
- JWT令牌包含用户ID和邮箱信息
- 敏感信息不会在API响应中返回

### 备份建议

建议定期备份`data/users.json`文件：

```bash
# 创建备份
cp data/users.json data/users_backup_$(date +%Y%m%d_%H%M%S).json

# 或者备份整个data目录
tar -czf data_backup_$(date +%Y%m%d_%H%M%S).tar.gz data/
```

### 数据迁移

如果需要迁移到数据库系统，可以：

1. 读取`users.json`文件
2. 解析JSON数据
3. 插入到目标数据库

示例迁移脚本（伪代码）：

```python
import json
from your_db import create_user

# 读取JSON数据
with open('data/users.json', 'r') as f:
    users = json.load(f)

# 迁移到数据库
for user in users:
    create_user(
        username=user['username'],
        email=user['email'],
        hashed_password=user['hashed_password'],
        # ... 其他字段
    )
```

## 限制和注意事项

### 适用场景
- ✅ 个人使用
- ✅ 小规模团队（<10人）
- ✅ 开发和测试环境

### 不适用场景
- ❌ 高并发访问
- ❌ 大量用户（>100人）
- ❌ 生产环境多用户系统
- ❌ 需要复杂查询的场景

### 性能考虑
- 每次读写都会加载整个文件
- 用户数量过多会影响性能
- 没有索引，查询效率有限

### 并发限制
- 不支持并发写入
- 多个进程同时写入可能导致数据损坏
- 建议在单进程环境使用
