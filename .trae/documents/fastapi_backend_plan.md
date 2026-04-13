# FastAPI 后端实现计划

## 一、项目概述

为试卷讲解Demo项目创建一个FastAPI后端,提供细粒度的RESTful API接口来调用现有的处理脚本。每个处理步骤都可以独立调用和控制。

## 二、技术栈

* **框架**: FastAPI

* **任务队列**: 异步任务 (asyncio) + 后台任务

* **文件处理**: 临时文件管理 + output目录

* **API文档**: 自动生成Swagger UI

* **依赖管理**: requirements.txt

## 三、核心功能模块

### 1. 细粒度API端点设计

**文件管理:**

* `POST /api/v1/files/upload` - 上传PDF或图片文件

* `GET /api/v1/files` - 列出所有已上传的文件

* `GET /api/v1/files/{file_id}` - 获取文件信息

* `GET /api/v1/files/{file_id}/download` - 下载原始文件

* `DELETE /api/v1/files/{file_id}` - 删除文件

**MinerU提取:**

* `POST /api/v1/mineru/extract` - 对上传的文件启动MinerU提取任务

* `GET /api/v1/mineru/tasks/{task_id}` - 查询MinerU提取任务状态

* `GET /api/v1/mineru/tasks/{task_id}/result` - 获取MinerU提取结果(JSON)

* `GET /api/v1/mineru/results/{file_id}` - 获取指定文件的MinerU结果

* `POST /api/v1/mineru/batch-extract` - 批量启动MinerU提取

**DeepSeek修复:**

* `POST /api/v1/deepseek/fix` - 对MinerU提取的JSON进行DeepSeek修复

* `GET /api/v1/deepseek/tasks/{task_id}` - 查询DeepSeek修复任务状态

* `GET /api/v1/deepseek/tasks/{task_id}/result` - 获取DeepSeek修复后的完整JSON

* `POST /api/v1/deepseek/batch-fix` - 批量启动DeepSeek修复

**PPT生成:**

* `POST /api/v1/ppt/generate` - 从JSON文件生成PPT

* `GET /api/v1/ppt/tasks/{task_id}` - 查询PPT生成任务状态

* `GET /api/v1/ppt/tasks/{task_id}/result` - 获取PPT生成结果

* `GET /api/v1/ppt/results/{json_file_id}` - 获取指定JSON生成的PPT

* `POST /api/v1/ppt/batch-generate` - 批量生成PPT

**相似题生成:**

* `POST /api/v1/questions/{task_id}/{question_index}/generate-similar` - 对指定题目生成相似题

* `GET /api/v1/questions/similar-tasks/{task_id}` - 查询相似题生成任务状态

* `GET /api/v1/questions/similar-tasks/{task_id}/result` - 获取生成的相似题结果

* `POST /api/v1/questions/{task_id}/{question_index}/batch-generate` - 批量生成多道相似题

**完整管道:**

* `POST /api/v1/pipeline/full` - 完整流程:上传→提取→修复→生成PPT

* `POST /api/v1/pipeline/upload-and-extract` - 上传+提取

* `POST /api/v1/pipeline/extract-and-fix` - 提取+修复

* `POST /api/v1/pipeline/fix-and-generate` - 修复+生成PPT

**文件下载:**

* `GET /api/v1/download/json/{task_id}` - 下载DeepSeek修复后的JSON

* `GET /api/v1/download/ppt/{task_id}` - 下载生成的PPT

* `GET /api/v1/download/raw/{task_id}` - 下载MinerU提取的原始JSON

**任务管理:**

* `GET /api/v1/tasks` - 列出所有任务(支持分页、过滤)

* `GET /api/v1/tasks/{task_id}` - 获取任务详细信息

* `DELETE /api/v1/tasks/{task_id}` - 删除任务及关联文件

* `POST /api/v1/tasks/{task_id}/retry` - 重试失败的任务

**健康检查:**

* `GET /api/v1/health` - 服务健康状态

* `GET /api/v1/health/ready` - 就绪检查

## 四、API端点详细设计

### 4.1 文件管理接口

#### POST /api/v1/files/upload

**功能:** 上传PDF或图片文件

**请求:**

* Content-Type: multipart/form-data

* Body: file (必填)

**响应:**

```json
{
  "file_id": "uuid",
  "filename": "test.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "upload_time": "2024-01-01T12:00:00Z",
  "status": "uploaded"
}
```

#### GET /api/v1/files

**功能:** 列出所有已上传的文件

**查询参数:**

* page: int (默认1)

* limit: int (默认20,最大100)

* file\_type: "pdf" | "image" | "all" (默认all)

**响应:**

```json
{
  "total": 50,
  "page": 1,
  "limit": 20,
  "files": [
    {
      "file_id": "uuid",
      "filename": "test.pdf",
      "file_type": "pdf",
      "upload_time": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### 4.2 MinerU提取接口

#### POST /api/v1/mineru/extract

**功能:** 对上传的文件启动MinerU提取

**请求:**

```json
{
  "file_id": "uuid"
}
```

**响应:**

```json
{
  "task_id": "uuid",
  "file_id": "uuid",
  "status": "pending",
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### GET /api/v1/mineru/tasks/{task\_id}/result

**功能:** 获取MinerU提取结果

**响应:**

```json
{
  "task_id": "uuid",
  "status": "completed",
  "result_file": "/output/xxx_content_list.json",
  "questions_count": 20,
  "data": {
    "source": "试卷名称",
    "questions": [...]
  }
}
```

### 4.3 DeepSeek修复接口

#### POST /api/v1/deepseek/fix

**功能:** 对MinerU提取的JSON进行DeepSeek修复

**请求:**

```json
{
  "minerU_task_id": "uuid",
  "use_existing_file": false
}
```

或使用已有文件:

```json
{
  "json_file_path": "output/xxx_content_list.json",
  "use_existing_file": true
}
```

**响应:**

```json
{
  "task_id": "uuid",
  "status": "pending",
  "source": "minerU_task_id" | "file_path",
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### GET /api/v1/deepseek/tasks/{task\_id}/result

**功能:** 获取DeepSeek修复后的完整JSON数据

**响应:**

```json
{
  "task_id": "uuid",
  "status": "completed",
  "result_file": "/output/xxx_content_list_cleaned.json",
  "questions_count": 20,
  "json_content": {
    "source": "试卷名称",
    "questions": [
      {
        "title": "第1题",
        "source": "试卷名称",
        "content": "题目内容...",
        "answer": "答案",
        "analysis": "解析"
      }
    ]
  },
  "data": {
    "source": "试卷名称",
    "questions": [...]
  }
}
```

### 4.4 PPT生成接口

#### POST /api/v1/ppt/generate

**功能:** 从JSON文件生成PPT

**请求:**

```json
{
  "json_file_path": "output/xxx_content_list_cleaned.json",
  "use_animation": true,
  "title": "C++期末试卷评讲"
}
```

**响应:**

```json
{
  "task_id": "uuid",
  "status": "pending",
  "input_json": "output/xxx_content_list_cleaned.json",
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### GET /api/v1/ppt/tasks/{task\_id}/result

**功能:** 获取PPT生成结果

**响应:**

```json
{
  "task_id": "uuid",
  "status": "completed",
  "pptx_file": "/output/xxx_fixed.pptx",
  "slide_count": 21,
  "questions_count": 20
}
```

### 4.5 相似题生成接口

#### POST /api/v1/questions/{task_id}/{question_index}/generate-similar

**功能:** 对指定题目生成相似题（调用DeepSeek AI）

**路径参数:**

* task_id: DeepSeek任务的ID
* question_index: 题目索引（从0开始）

**请求:**

```json
{
  "count": 1,
  "difficulty_adjustment": "same",
  "preserve_knowledge_points": true
}
```

**参数说明:**

* count: 生成相似题数量（默认1，最多5）
* difficulty_adjustment: 难度调整 "easier" | "same" | "harder"（默认same）
* preserve_knowledge_points: 是否保留原知识点（默认true）

**响应:**

```json
{
  "task_id": "uuid",
  "status": "pending",
  "source_question": {
    "index": 0,
    "title": "第1题",
    "content": "题目内容..."
  },
  "generation_config": {
    "count": 1,
    "difficulty_adjustment": "same"
  },
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### GET /api/v1/questions/similar-tasks/{task_id}

**功能:** 查询相似题生成任务状态

**响应:**

```json
{
  "task_id": "uuid",
  "status": "processing",
  "progress": 50,
  "current_step": "正在调用DeepSeek API生成相似题...",
  "source_question": {
    "index": 0,
    "title": "第1题"
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:01:30Z"
}
```

#### GET /api/v1/questions/similar-tasks/{task_id}/result

**功能:** 获取生成的相似题结果

**响应:**

```json
{
  "task_id": "uuid",
  "status": "completed",
  "source_question": {
    "index": 0,
    "title": "第1题",
    "content": "原题内容...",
    "answer": "原题答案",
    "analysis": "原题解析"
  },
  "similar_questions": [
    {
      "title": "相似题1",
      "content": "相似题内容...",
      "answer": "相似题答案",
      "analysis": "相似题解析",
      "difficulty": "same",
      "knowledge_points": ["知识点1", "知识点2"]
    }
  ],
  "generated_count": 1,
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:02:00Z"
}
```

#### POST /api/v1/questions/{task_id}/batch-generate

**功能:** 批量生成多道相似题

**请求:**

```json
{
  "question_indices": [0, 2, 5],
  "count_per_question": 2,
  "difficulty_adjustment": "same"
}
```

**响应:**

```json
{
  "batch_task_id": "uuid",
  "tasks": [
    {"question_index": 0, "similar_task_id": "uuid"},
    {"question_index": 2, "similar_task_id": "uuid"},
    {"question_index": 5, "similar_task_id": "uuid"}
  ],
  "total_questions": 6,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 4.6 管道接口

#### POST /api/v1/pipeline/full

**功能:** 完整流程(上传→提取→修复→生成PPT)

**请求:**

* Content-Type: multipart/form-data

* Body: file (必填), use\_animation (可选,默认true)

**响应:**

```json
{
  "pipeline_id": "uuid",
  "stages": {
    "upload": {"task_id": "uuid", "status": "completed"},
    "minerU": {"task_id": "uuid", "status": "processing"},
    "deepseek": {"task_id": "uuid", "status": "pending"},
    "ppt": {"task_id": "uuid", "status": "pending"}
  },
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### GET /api/v1/pipeline/{pipeline\_id}

**功能:** 查询完整管道的所有阶段状态

**响应:**

```json
{
  "pipeline_id": "uuid",
  "stages": {
    "upload": {"task_id": "uuid", "status": "completed"},
    "minerU": {"task_id": "uuid", "status": "completed"},
    "deepseek": {
      "task_id": "uuid",
      "status": "completed",
      "result_file": "/output/xxx_content_list_cleaned.json"
    },
    "ppt": {
      "task_id": "uuid",
      "status": "completed",
      "pptx_file": "/output/xxx_fixed.pptx"
    }
  },
  "all_completed": true
}
```

### 4.7 文件下载接口

#### GET /api/v1/download/json/{task\_id}

**功能:** 下载DeepSeek修复后的JSON文件

**响应:**

* Content-Type: application/json

* Content-Disposition: attachment; filename="xxx\_content\_list\_cleaned.json"

* 文件内容

#### GET /api/v1/download/ppt/{task\_id}

**功能:** 下载生成的PPT文件

**响应:**

* Content-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation

* Content-Disposition: attachment; filename="xxx\_fixed.pptx"

* 文件内容

## 五、数据模型

### File模型

```python
class UploadedFile:
    file_id: str
    filename: str
    file_type: str  # "pdf" | "image"
    file_size: int
    file_path: str
    upload_time: datetime
    status: str  # "uploaded" | "processing" | "completed" | "deleted"
```

### MinerUTask模型

```python
class MinerUTask:
    task_id: str
    file_id: str
    status: TaskStatus  # pending, processing, completed, failed
    progress: int
    current_step: str
    result_file: str | None
    error: str | None
    created_at: datetime
    updated_at: datetime
```

### DeepSeekTask模型

```python
class DeepSeekTask:
    task_id: str
    source_type: str  # "minerU_task" | "file_path"
    source_id: str  # task_id或文件路径
    status: TaskStatus
    progress: int
    result_file: str | None
    json_content: dict | None  # 完整的JSON数据
    error: str | None
    created_at: datetime
    updated_at: datetime
```

### PPTTask模型

```python
class PPTTask:
    task_id: str
    json_file_path: str
    use_animation: bool
    title: str | None
    status: TaskStatus
    progress: int
    pptx_file: str | None
    slide_count: int | None
    error: str | None
    created_at: datetime
    updated_at: datetime
```

### SimilarQuestionTask模型
```python
class SimilarQuestionTask:
    task_id: str
    source_task_id: str  # 关联的DeepSeek任务ID
    question_index: int  # 源题目索引
    count: int  # 生成数量
    difficulty_adjustment: str  # "easier" | "same" | "harder"
    preserve_knowledge_points: bool
    status: TaskStatus
    progress: int
    source_question: dict | None  # 源题目完整数据
    similar_questions: List[dict] | None  # 生成的相似题列表
    error: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
```

### Pipeline模型

```python
class Pipeline:
    pipeline_id: str
    stages: dict  # {stage_name: {task_id, status, result}}
    created_at: datetime
    updated_at: datetime
```

## 六、目录结构

```
试卷讲解demo/
├── app.py                    # FastAPI应用入口
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── files.py          # 文件上传下载
│   │   ├── mineru.py         # MinerU提取
│   │   ├── deepseek.py        # DeepSeek修复
│   │   ├── ppt.py            # PPT生成
│   │   ├── questions.py      # 相似题生成
│   │   ├── pipeline.py        # 完整管道
│   │   ├── tasks.py          # 任务管理
│   │   └── health.py         # 健康检查
│   └── models/
│       ├── __init__.py
│       └── schemas.py         # Pydantic模型
├── services/
│   ├── __init__.py
│   ├── mineru_service.py      # MinerU处理逻辑
│   ├── deepseek_service.py   # DeepSeek修复逻辑
│   ├── ppt_service.py        # PPT生成逻辑
│   ├── similar_question_service.py  # 相似题生成逻辑
│   └── task_manager.py       # 任务状态管理
├── utils/
│   ├── __init__.py
│   ├── file_handler.py       # 文件处理工具
│   ├── storage.py            # 存储管理
│   └── config.py             # 配置管理
├── output/                   # 输出目录
├── temp/                     # 临时文件目录
├── requirements.txt
└── .env.example
```

## 七、实现步骤

### 阶段1: 基础设施

1. 创建目录结构
2. 创建requirements.txt
3. 创建.env.example
4. 实现配置管理 (config.py)
5. 实现文件存储管理 (storage.py)

### 阶段2: 核心服务层

1. 实现任务管理器 (task\_manager.py) - 统一的任务状态管理
2. 实现文件处理器 (file\_handler.py) - 文件上传、验证、清理
3. 实现MinerU服务 (mineru\_service.py)
4. 实现DeepSeek服务 (deepseek\_service.py)
5. 实现PPT生成服务 (ppt\_service.py)
6. 实现相似题生成服务 (similar\_question\_service.py) - 调用DeepSeek生成相似题

### 阶段3: API层

1. 实现Pydantic模型 (schemas.py)
2. 实现文件管理API (files.py)
3. 实现MinerU API (mineru.py)
4. 实现DeepSeek API (deepseek.py)
5. 实现PPT API (ppt.py)
6. 实现相似题API (questions.py)
7. 实现管道API (pipeline.py)
8. 实现任务管理API (tasks.py)
9. 实现健康检查API (health.py)
10. 创建应用入口 (app.py)

### 阶段4: 集成测试

1. 单元测试
2. API端点测试
3. 端到端测试

## 八、关键实现细节

### 8.1 异步任务处理

使用FastAPI的BackgroundTasks处理长时间运行的任务:

```python
@router.post("/mineru/extract")
async def start_mineru_extraction(request: MinerUExtractRequest, background_tasks: BackgroundTasks):
    task = create_mineru_task(file_id=request.file_id)
    background_tasks.add_task(run_mineru_extraction, task.task_id)
    return {"task_id": task.task_id, "status": "pending"}

@router.post("/deepseek/fix")
async def start_deepseek_fix(request: DeepSeekFixRequest, background_tasks: BackgroundTasks):
    task = create_deepseek_task(source_type=request.source_type, source_id=request.source_id)
    background_tasks.add_task(run_deepseek_fix, task.task_id)
    return {"task_id": task.task_id, "status": "pending"}

@router.post("/ppt/generate")
async def generate_ppt(request: PPTGenerateRequest, background_tasks: BackgroundTasks):
    task = create_ppt_task(json_file_path=request.json_file_path, use_animation=request.use_animation)
    background_tasks.add_task(run_ppt_generation, task.task_id)
    return {"task_id": task.task_id, "status": "pending"}
```

### 8.2 返回完整JSON数据

DeepSeek修复完成后,需要加载并返回完整JSON内容:

```python
@router.get("/deepseek/tasks/{task_id}/result")
async def get_deepseek_result(task_id: str):
    task = get_deepseek_task(task_id)
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="任务未完成")
    
    json_content = None
    if task.result_file:
        json_path = Path(task.result_file)
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                json_content = json.load(f)
    
    return {
        "task_id": task_id,
        "status": "completed",
        "result_file": task.result_file,
        "questions_count": len(json_content.get("questions", [])) if json_content else 0,
        "json_content": json_content,
        "data": json_content
    }
```

### 8.3 文件下载

```python
@router.get("/download/json/{task_id}")
async def download_json(task_id: str):
    task = get_deepseek_task(task_id)
    if not task.result_file or not Path(task.result_file).exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=task.result_file,
        filename=Path(task.result_file).name,
        media_type="application/json"
    )

@router.get("/download/ppt/{task_id}")
async def download_ppt(task_id: str):
    task = get_ppt_task(task_id)
    if not task.pptx_file or not Path(task.pptx_file).exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=task.pptx_file,
        filename=Path(task.pptx_file).name,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
```

### 8.4 批量处理

```python
@router.post("/mineru/batch-extract")
async def batch_mineru_extract(request: BatchMinerUExtractRequest, background_tasks: BackgroundTasks):
    tasks = []
    for file_id in request.file_ids:
        task = create_mineru_task(file_id=file_id)
        background_tasks.add_task(run_mineru_extraction, task.task_id)
        tasks.append({"file_id": file_id, "task_id": task.task_id})
    
    return {
        "total": len(tasks),
        "tasks": tasks
    }
```

### 8.5 相似题生成

相似题生成功能通过调用DeepSeek API,基于原题目生成具有相同知识点但数据或表述不同的相似题:

```python
@router.post("/questions/{task_id}/{question_index}/generate-similar")
async def generate_similar_question(
    task_id: str,
    question_index: int,
    request: GenerateSimilarRequest,
    background_tasks: BackgroundTasks
):
    deepseek_task = get_deepseek_task(task_id)
    if deepseek_task.status != "completed":
        raise HTTPException(status_code=400, detail="DeepSeek任务未完成")
    
    source_question = deepseek_task.json_content["questions"][question_index]
    
    task = create_similar_question_task(
        source_task_id=task_id,
        question_index=question_index,
        source_question=source_question,
        count=request.count,
        difficulty_adjustment=request.difficulty_adjustment
    )
    
    background_tasks.add_task(run_similar_question_generation, task.task_id)
    return {"task_id": task.task_id, "status": "pending", "source_question": source_question}
```

生成相似题的核心逻辑:

```python
async def run_similar_question_generation(task_id: str):
    task = get_similar_question_task(task_id)
    update_task_status(task_id, "processing", progress=10)
    
    difficulty_prompt = ""
    if task.difficulty_adjustment == "easier":
        difficulty_prompt = "请生成难度较低的相似题,侧重基础知识点"
    elif task.difficulty_adjustment == "harder":
        difficulty_prompt = "请生成难度较高的相似题,增加综合性或创新性"
    else:
        difficulty_prompt = "请生成难度相同的相似题"
    
    prompt = f"""
请根据以下原题生成{task.count}道相似题。

原题信息:
- 标题: {task.source_question['title']}
- 内容: {task.source_question['content']}
- 答案: {task.source_question['answer']}
- 解析: {task.source_question['analysis']}

{difficulty_prompt}

要求:
1. 保持相同的知识点和题型
2. 改变数据、情境或表述方式
3. 每道题必须包含: title, content, answer, analysis字段
4. 以JSON数组格式返回结果

返回格式:
{{"similar_questions": [{{"title": "...", "content": "...", "answer": "...", "analysis": "..."}}]}}
"""
    
    update_task_status(task_id, "processing", progress=30)
    
    client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("API_URL"))
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    update_task_status(task_id, "processing", progress=70)
    
    result = json.loads(response.choices[0].message.content)
    similar_questions = result.get("similar_questions", [])
    
    update_similar_questions(task_id, similar_questions)
    update_task_status(task_id, "completed", progress=100)
```

获取相似题结果:

```python
@router.get("/questions/similar-tasks/{task_id}/result")
async def get_similar_question_result(task_id: str):
    task = get_similar_question_task(task_id)
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="任务未完成")
    
    return {
        "task_id": task_id,
        "status": "completed",
        "source_question": task.source_question,
        "similar_questions": task.similar_questions,
        "generated_count": len(task.similar_questions),
        "created_at": task.created_at,
        "completed_at": task.completed_at
    }
```

## 九、依赖包

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
pydantic>=2.0.0
python-pptx>=0.6.21
openai>=1.0.0
python-dotenv>=1.0.0
aiofiles>=23.0.0
```

## 十、扩展建议

1. 添加数据库持久化 (SQLite/PostgreSQL)
2. 添加Redis缓存
3. 添加用户认证和授权
4. 添加任务优先级队列
5. 添加WebSocket实时进度推送
6. 添加Docker容器化部署
7. 添加API限流和配额管理

