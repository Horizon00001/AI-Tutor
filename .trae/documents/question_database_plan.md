# 题目数据库存储方案

## 一、需求分析

当前题目数据以JSON文件形式存储，添加数据库存储后可以实现：
- 题目与用户关联（每个用户只能看到自己的题目）
- 题目的持久化存储和查询
- 支持题目的增删改查操作
- 便于后续扩展（题目分类、标签、搜索等）

## 二、数据库表结构设计

### 1. exams 表（试卷表）
| 字段 | 类型 | 说明 |
|------|------|------|
| exam_id | TEXT (PK) | 试卷UUID |
| user_id | TEXT (FK) | 所属用户ID |
| source | TEXT | 试卷来源/名称 |
| raw_json_path | TEXT | 原始JSON文件路径 |
| cleaned_json_path | TEXT | 清洗后JSON文件路径 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 2. questions 表（题目表）
| 字段 | 类型 | 说明 |
|------|------|------|
| question_id | TEXT (PK) | 题目UUID |
| exam_id | TEXT (FK) | 所属试卷ID |
| user_id | TEXT (FK) | 所属用户ID |
| title | TEXT | 题目编号（如"第1题"） |
| content | TEXT | 题目内容 |
| answer | TEXT | 答案 |
| analysis | TEXT | 解析 |
| options | TEXT | 选项（JSON格式存储） |
| question_index | INTEGER | 在试卷中的序号 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 3. similar_questions 表（相似题表）
| 字段 | 类型 | 说明 |
|------|------|------|
| similar_id | TEXT (PK) | 相似题UUID |
| source_question_id | TEXT (FK) | 原题目ID |
| exam_id | TEXT (FK) | 所属试卷ID |
| user_id | TEXT (FK) | 所属用户ID |
| title | TEXT | 相似题标题 |
| content | TEXT | 相似题内容 |
| answer | TEXT | 相似题答案 |
| analysis | TEXT | 相似题解析 |
| difficulty | TEXT | 难度等级 |
| created_at | TIMESTAMP | 创建时间 |

## 三、实现步骤

### 步骤1：更新数据库模块
修改 `services/database.py`：
- 添加 `init_question_tables()` 函数
- 添加试卷相关CRUD函数
- 添加题目相关CRUD函数
- 添加相似题相关CRUD函数

### 步骤2：创建试卷和题目服务
新建 `services/exam_service.py`：
- `create_exam(user_id, source)` - 创建试卷记录
- `get_exam_by_id(exam_id, user_id)` - 获取试卷
- `list_user_exams(user_id, page, limit)` - 列出用户试卷
- `add_questions_to_exam(exam_id, questions)` - 添加题目到试卷
- `get_questions_by_exam(exam_id)` - 获取试卷所有题目

### 步骤3：创建相似题存储服务
修改 `services/similar_question_service.py`：
- 保存相似题到数据库
- 查询用户的相似题

### 步骤4：创建API路由
新建 `api/routes/exams.py`：
- `POST /api/v1/exams` - 创建试卷
- `GET /api/v1/exams` - 列出用户试卷
- `GET /api/v1/exams/{exam_id}` - 获取试卷详情
- `GET /api/v1/exams/{exam_id}/questions` - 获取试卷题目
- `PUT /api/v1/exams/{exam_id}/questions/{question_id}` - 更新题目
- `DELETE /api/v1/exams/{exam_id}` - 删除试卷

### 步骤5：修改现有路由添加用户关联
修改以下路由，添加用户隔离：
- `pipeline.py` - 处理完成后保存到数据库
- `questions.py` - 相似题保存到数据库
- `files.py` - 文件关联用户

### 步骤6：更新 app.py
注册 exams 路由

## 四、数据迁移

现有JSON文件中的题目可以迁移到数据库：
```python
def migrate_existing_questions():
    # 读取 output/processed_json/*.json
    # 为每个文件创建 exam 记录
    # 解析题目并创建 question 记录
```

## 五、API接口设计

### POST /api/v1/exams

**功能**：创建试卷（从已处理的JSON文件）

**请求**：
```json
{
  "source": "21年计网期末试卷",
  "cleaned_json_path": "output/processed_json/xxx_content_list_cleaned.json"
}
```

**响应**：
```json
{
  "exam_id": "uuid",
  "source": "21年计网期末试卷",
  "questions_count": 20,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### GET /api/v1/exams

**功能**：列出用户的所有试卷

**响应**：
```json
{
  "total": 5,
  "page": 1,
  "limit": 20,
  "exams": [
    {
      "exam_id": "uuid",
      "source": "21年计网期末试卷",
      "questions_count": 20,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### GET /api/v1/exams/{exam_id}/questions

**功能**：获取试卷的所有题目

**响应**：
```json
{
  "exam_id": "uuid",
  "source": "21年计网期末试卷",
  "questions": [
    {
      "question_id": "uuid",
      "title": "1",
      "content": "【单选题】...",
      "answer": "B",
      "analysis": "知识点解析..."
    }
  ]
}
```

### PUT /api/v1/exams/{exam_id}/questions/{question_id}

**功能**：更新题目内容（用于教师修改）

**请求**：
```json
{
  "content": "修改后的题目内容",
  "answer": "修改后的答案",
  "analysis": "修改后的解析"
}
```

## 六、需要修改的文件

1. 修改 `services/database.py` - 添加题目相关表和函数
2. 新建 `services/exam_service.py` - 试卷服务
3. 新建 `api/routes/exams.py` - 试卷API路由
4. 修改 `services/similar_question_service.py` - 保存相似题到数据库
5. 修改 `api/routes/pipeline.py` - 完成后保存到数据库
6. 修改 `app.py` - 注册 exams 路由

## 七、安全考虑

1. 所有题目查询都通过 user_id 过滤
2. 验证用户对试卷的所有权
3. 敏感操作记录审计日志
