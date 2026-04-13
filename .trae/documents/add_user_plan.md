# 添加用户系统计划

## 一、需求分析

当前系统没有用户认证功能，所有API请求都是公开的。添加用户系统后，可以实现：
- 用户注册与登录
- 用户数据隔离（每个用户只能看到自己的文件、任务）
- 操作审计追踪

## 二、技术方案

### 方案选择：JWT + SQLite 轻量级方案

**理由**：
- 项目规模适中，无需复杂的企业级认证
- SQLite 无需额外数据库服务
- JWT 无状态认证，便于扩展
- 与现有 FastAPI 架构无缝集成

## 三、实现步骤

### 步骤1：安装依赖

```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

### 步骤2：创建用户数据模型

新建 `api/models/user.py`:
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class User(BaseModel):
    user_id: str
    username: str
    email: str
    hashed_password: str
    created_at: datetime
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
```

### 步骤3：创建用户服务

新建 `services/user_service.py`:
- `hash_password(password)` - 密码加密
- `verify_password(plain_password, hashed_password)` - 密码验证
- `create_access_token(data)` - 生成JWT token
- `register_user(user_data)` - 用户注册
- `authenticate_user(username, password)` - 用户登录验证
- `get_user_by_id(user_id)` - 获取用户信息

### 步骤4：创建认证路由

新建 `api/routes/auth.py`:
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息

### 步骤5：修改现有路由添加用户隔离

修改以下路由，添加 `user_id` 字段：
- `files.py` - 上传文件时关联用户
- `tasks.py` - 查询任务时过滤用户
- 其他需要用户隔离的路由

### 步骤6：更新 app.py

在 `app.py` 中：
1. 导入 auth 路由
2. 添加 auth 路由注册

### 步骤7：添加认证中间件

可选：添加全局认证依赖，限制未登录访问。

## 四、数据库表设计

```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

## 五、安全考虑

1. 密码使用 bcrypt 加密存储
2. JWT token 设置过期时间（24小时）
3. 敏感操作需要重新验证密码
4. CORS 配置可根据需求调整

## 六、API 接口设计

### POST /api/v1/auth/register

**请求**:
```json
{
  "username": "teacher1",
  "email": "teacher1@school.com",
  "password": "securepassword123"
}
```

**响应**:
```json
{
  "user_id": "uuid",
  "username": "teacher1",
  "email": "teacher1@school.com",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### POST /api/v1/auth/login

**请求**:
```json
{
  "username": "teacher1",
  "password": "securepassword123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### GET /api/v1/auth/me

**Headers**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "user_id": "uuid",
  "username": "teacher1",
  "email": "teacher1@school.com",
  "created_at": "2024-01-01T12:00:00Z"
}
```

## 七、需要修改的文件清单

1. 新建 `api/models/user.py`
2. 新建 `services/user_service.py`
3. 新建 `api/routes/auth.py`
4. 修改 `app.py` - 添加 auth 路由
5. 修改 `requirements.txt` - 添加依赖
6. 可选：创建 `services/database.py` - 数据库连接管理

## 八、后续扩展

1. 添加管理员功能（用户管理）
2. 添加角色权限控制
3. 添加登录日志
4. 添加密码重置功能
5. 集成第三方登录（OAuth）
