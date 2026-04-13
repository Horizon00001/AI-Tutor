# 数据库管理方案

## 一、当前实现

已创建的数据库相关文件：
- `services/database.py` - 数据库管理模块
- 数据库文件位置：`data.db`（项目根目录）

## 二、数据库表结构

### users 表
| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | TEXT (PRIMARY KEY) | 用户UUID |
| username | TEXT (UNIQUE) | 用户名 |
| email | TEXT (UNIQUE) | 邮箱 |
| hashed_password | TEXT | 加密后的密码 |
| created_at | TIMESTAMP | 创建时间 |
| is_active | BOOLEAN | 是否激活 |

## 三、数据库初始化

数据库会在首次调用认证API时自动初始化（调用 `init_db()`）。

手动初始化方式：
```python
from services.database import init_db
init_db()
```

## 四、数据文件位置

- 开发环境：`f:\大二下学期\杂项\ai教育\试卷讲解demo\data.db`
- 数据文件已添加到 `.gitignore`（避免提交用户数据）

## 五、后续扩展建议

### 1. 添加用户任务表（user_tasks）
```sql
CREATE TABLE user_tasks (
    task_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### 2. 添加用户文件表（user_files）
```sql
CREATE TABLE user_files (
    file_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### 3. 数据库备份
```bash
# 备份数据库
copy data.db data_backup.db

# 定期备份脚本（可选）
```

### 4. 数据库迁移工具
如需添加更多表，建议创建 `services/migration.py` 来管理数据库版本。

## 六、当前可用的数据库操作

```python
from services.database import init_db, create_user, get_user_by_username, get_user_by_email, get_user_by_id

# 初始化数据库
init_db()

# 创建用户
create_user(user_id, username, email, hashed_password)

# 查询用户
get_user_by_username("teacher1")
get_user_by_email("teacher1@school.com")
get_user_by_id("uuid-string")
```
