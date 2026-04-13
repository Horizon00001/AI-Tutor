# 如何添加新功能 - 开发指南

## 项目架构概览

本项目采用 **FastAPI + SQLite** 架构，遵循分层设计模式：

```
试卷讲解Demo/
├── app.py                 # 应用入口，注册所有路由
├── api/
│   ├── models/
│   │   ├── schemas.py     # Pydantic数据模型（请求/响应）
│   │   └── user.py        # 用户相关模型
│   └── routes/
│       ├── __init__.py    # 路由导出
│       ├── auth.py        # 认证路由
│       ├── exams.py       # 试卷管理路由
│       ├── questions.py   # 题目管理路由
│       ├── ppt.py         # PPT生成路由
│       └── ...            # 其他路由
├── services/
│   ├── exam_service.py    # 试卷业务逻辑
│   ├── ppt_service.py     # PPT生成逻辑
│   ├── database.py        # 数据库操作
│   └── ...                # 其他服务
├── utils/
│   ├── config.py          # 配置管理
│   └── ...                # 工具函数
└── output/                # 输出文件目录
```

---

## 添加新功能的步骤

### 步骤1：分析需求，确定功能类型

首先明确你要添加的功能属于哪种类型：

| 功能类型 | 示例 | 需要修改的文件 |
|---------|------|--------------|
| **数据模型** | 新增字段、新表结构 | `schemas.py`, `database.py` |
| **API接口** | 新增接口、修改接口 | `routes/` 下新建或修改 |
| **业务逻辑** | 数据处理、算法实现 | `services/` 下新建或修改 |
| **工具函数** | 通用功能、辅助函数 | `utils/` 下新建 |

---

### 步骤2：定义数据模型（schemas.py）

在 `api/models/schemas.py` 中添加请求和响应模型：

```python
# 示例：添加"错题本"功能的数据模型

class AddToWrongBookRequest(BaseModel):
    """添加到错题本的请求"""
    question_id: str
    wrong_reason: Optional[str] = None
    notes: Optional[str] = None

class WrongBookItemResponse(BaseModel):
    """错题本条目响应"""
    item_id: str
    question_id: str
    question_content: str
    wrong_reason: Optional[str]
    notes: Optional[str]
    added_at: datetime

class ListWrongBookResponse(BaseModel):
    """错题本列表响应"""
    total: int
    items: List[WrongBookItemResponse]
```

**注意事项：**
- 所有模型继承自 `BaseModel`
- 使用 `Optional` 标记可选字段
- 使用 `Field()` 添加验证规则（如 `ge=1` 表示大于等于1）

---

### 步骤3：实现数据库操作（services/database.py）

在 `services/database.py` 中添加数据库表和操作方法：

```python
# 1. 在 init_db() 函数中添加新表

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ... 现有表 ...
    
    # 新增：错题本表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wrong_book (
            item_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            wrong_reason TEXT,
            notes TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (question_id) REFERENCES questions (question_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# 2. 添加数据库操作函数

def add_to_wrong_book(item_id: str, user_id: str, question_id: str, 
                      wrong_reason: str = None, notes: str = None) -> bool:
    """添加题目到错题本"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO wrong_book (item_id, user_id, question_id, wrong_reason, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_id, user_id, question_id, wrong_reason, notes))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"添加到错题本失败: {e}")
        return False

def get_wrong_book_by_user(user_id: str, page: int = 1, limit: int = 20) -> Tuple[int, List[Dict]]:
    """获取用户的错题本列表"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取总数
    cursor.execute('SELECT COUNT(*) FROM wrong_book WHERE user_id = ?', (user_id,))
    total = cursor.fetchone()[0]
    
    # 获取分页数据
    offset = (page - 1) * limit
    cursor.execute('''
        SELECT w.*, q.content as question_content 
        FROM wrong_book w
        JOIN questions q ON w.question_id = q.question_id
        WHERE w.user_id = ?
        ORDER BY w.added_at DESC
        LIMIT ? OFFSET ?
    ''', (user_id, limit, offset))
    
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return total, items
```

---

### 步骤4：实现业务逻辑（services/下新建文件）

创建 `services/wrong_book_service.py`：

```python
import uuid
from typing import Dict, List, Optional
from services.database import add_to_wrong_book, get_wrong_book_by_user

def add_question_to_wrong_book(user_id: str, question_id: str, 
                                wrong_reason: str = None, notes: str = None) -> Dict:
    """添加题目到错题本的业务逻辑"""
    item_id = str(uuid.uuid4())
    
    success = add_to_wrong_book(item_id, user_id, question_id, wrong_reason, notes)
    
    if not success:
        return {"success": False, "error": "添加失败，题目可能已存在"}
    
    return {
        "success": True,
        "item_id": item_id,
        "message": "已成功添加到错题本"
    }

def get_user_wrong_book(user_id: str, page: int = 1, limit: int = 20) -> Dict:
    """获取用户错题本列表"""
    total, items = get_wrong_book_by_user(user_id, page, limit)
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": items
    }
```

---

### 步骤5：创建API路由（api/routes/下新建文件）

创建 `api/routes/wrong_book.py`：

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from api.models.schemas import AddToWrongBookRequest, ListWrongBookResponse
from api.routes.auth import get_current_user
from services.wrong_book_service import add_question_to_wrong_book, get_user_wrong_book
from services.database import init_db

router = APIRouter(prefix="/wrong-book", tags=["错题本"])

@router.post("", response_model=Dict)
async def add_to_wrong_book(
    request: AddToWrongBookRequest,
    current_user: dict = Depends(get_current_user)
):
    """添加题目到错题本"""
    init_db()
    
    result = add_question_to_wrong_book(
        user_id=current_user["user_id"],
        question_id=request.question_id,
        wrong_reason=request.wrong_reason,
        notes=request.notes
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("", response_model=ListWrongBookResponse)
async def list_wrong_book(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """获取错题本列表"""
    init_db()
    
    result = get_user_wrong_book(current_user["user_id"], page, limit)
    return result
```

---

### 步骤6：注册路由（修改app.py和__init__.py）

**修改 `api/routes/__init__.py`：**

```python
from api.routes import files, mineru, deepseek, ppt, questions, pipeline, tasks, download, health, auth, exams, wrong_book
```

**修改 `app.py`：**

```python
from api.routes import files, mineru, deepseek, ppt, questions, pipeline, tasks, download, health, auth, exams, wrong_book

# ... 其他代码 ...

app.include_router(wrong_book.router, prefix="/api/v1")
```

---

### 步骤7：测试新功能

1. **重启服务器**：停止当前运行的 `app.py`，重新运行
2. **访问文档**：打开 `http://localhost:8080/docs` 查看新接口
3. **测试接口**：使用 Swagger UI 或 Postman 测试新功能

---

## 常见功能类型示例

### 类型A：简单CRUD功能（如错题本、收藏夹）

遵循完整的7个步骤：
1. 定义schemas
2. 创建数据库表和操作
3. 实现service层
4. 创建路由
5. 注册路由

### 类型B：扩展现有功能（如给试卷添加新字段）

只需要修改：
1. `schemas.py` - 添加新字段
2. `database.py` - 修改表结构（注意：SQLite不支持直接ALTER COLUMN，需要重建表）
3. 相关的service和route文件

### 类型C：调用外部API（如接入新的AI服务）

参考 `services/deepseek_service.py` 或 `services/mineru_service.py`：
1. 在 `utils/config.py` 添加配置项
2. 在 `services/` 创建服务文件
3. 在 `api/routes/` 创建路由

### 类型D：文件处理功能（如导入/导出）

参考 `api/routes/files.py` 和 `services/ppt_service.py`：
1. 使用 `utils/file_handler.py` 中的工具函数
2. 文件保存到 `uploads/` 或 `output/` 目录
3. 在数据库中记录文件路径

---

## 开发规范

### 命名规范

| 类型 | 命名方式 | 示例 |
|-----|---------|-----|
| 路由文件 | 名词，小写 | `wrong_book.py` |
| 服务文件 | 名词 + _service | `wrong_book_service.py` |
| 请求模型 | Request结尾 | `AddToWrongBookRequest` |
| 响应模型 | Response结尾 | `ListWrongBookResponse` |
| 路由前缀 | /api/v1/ + 名词 | `/api/v1/wrong-book` |

### 代码组织原则

1. **单一职责**：每个文件只做一件事
2. **分层清晰**：路由层只处理HTTP，业务逻辑放在service层
3. **复用优先**：通用功能提取到utils
4. **类型安全**：所有函数添加类型注解

### 数据库变更注意事项

SQLite 对表结构变更有一定限制：

```python
# 如果需要添加新列，使用：
ALTER TABLE table_name ADD COLUMN new_column TEXT

# 如果需要修改列类型，需要：
# 1. 创建新表
# 2. 迁移数据
# 3. 删除旧表
# 4. 重命名新表
```

---

## 快速检查清单

添加新功能前，确认以下事项：

- [ ] 功能需求清晰，知道需要哪些接口
- [ ] 数据模型已定义（schemas.py）
- [ ] 数据库表已设计（database.py）
- [ ] 业务逻辑已实现（services/）
- [ ] API路由已创建（routes/）
- [ ] 路由已在app.py注册
- [ ] 路由已在__init__.py导出
- [ ] 已测试接口可以正常访问

---

## 参考示例

本项目已有以下功能模块可供参考：

| 功能 | 参考文件 |
|-----|---------|
| 试卷管理 | `routes/exams.py`, `services/exam_service.py` |
| 题目管理 | `routes/questions.py` |
| PPT生成 | `routes/ppt.py`, `services/ppt_service.py` |
| 用户认证 | `routes/auth.py`, `services/user_service.py` |
| 文件上传 | `routes/files.py` |
| 任务管理 | `routes/tasks.py`, `services/task_manager.py` |

---

## 需要帮助？

如果你不确定如何添加某个功能，可以：

1. **查看相似功能**：找到项目中类似的功能模块作为参考
2. **遵循现有模式**：保持与现有代码一致的风格和结构
3. **逐步测试**：每完成一步就测试，确保正常工作

祝开发顺利！
