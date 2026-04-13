from fastapi import APIRouter, BackgroundTasks, HTTPException
from datetime import datetime
from pathlib import Path

from api.models.schemas import PPTGenerateRequest, PPTGenerateResponse, PPTResultResponse
from services.task_manager import task_manager, TaskType, TaskStatus
from services.ppt_service import ppt_service
from utils.storage import storage

router = APIRouter(prefix="/ppt", tags=["PPT生成"])

@router.post("/generate", response_model=PPTGenerateResponse)
async def generate_ppt(request: PPTGenerateRequest, background_tasks: BackgroundTasks):
    json_file_path = Path(request.json_file_path)
    if not json_file_path.exists():
        raise HTTPException(status_code=404, detail="JSON文件不存在")

    task = task_manager.create_task(TaskType.PPT, source_id=request.json_file_path)
    background_tasks.add_task(
        ppt_service.generate,
        json_file_path,
        request.use_animation,
        request.title or "试卷评讲",
        task.task_id
    )

    return PPTGenerateResponse(
        task_id=task.task_id,
        status=task.status.value,
        input_json=request.json_file_path,
        created_at=task.created_at
    )

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return task.to_dict()

@router.get("/tasks/{task_id}/result", response_model=PPTResultResponse)
async def get_ppt_result(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="任务未完成")

    return PPTResultResponse(
        task_id=task_id,
        status=task.status.value,
        pptx_file=task.result_file,
        slide_count=task.data.get("slide_count") if task.data else None,
        questions_count=task.data.get("questions_count") if task.data else None
    )

@router.get("/results/{json_file_id}")
async def get_ppt_by_json(json_file_id: str):
    ppt_path = storage.get_ppt(json_file_id)
    if not ppt_path:
        raise HTTPException(status_code=404, detail="PPT文件不存在")

    return {
        "json_file_id": json_file_id,
        "pptx_file": str(ppt_path)
    }

@router.post("/batch-generate")
async def batch_generate(request: dict, background_tasks: BackgroundTasks):
    json_file_paths = request.get("json_file_paths", [])
    use_animation = request.get("use_animation", True)
    title = request.get("title", "试卷评讲")

    tasks = []
    for json_path in json_file_paths:
        path = Path(json_path)
        if path.exists():
            task = task_manager.create_task(TaskType.PPT, source_id=json_path)
            background_tasks.add_task(ppt_service.generate, path, use_animation, title, task.task_id)
            tasks.append({"json_file_path": json_path, "task_id": task.task_id})

    return {
        "total": len(tasks),
        "tasks": tasks
    }
