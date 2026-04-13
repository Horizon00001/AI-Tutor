from fastapi import APIRouter, BackgroundTasks, HTTPException
from datetime import datetime
from pathlib import Path

from api.models.schemas import MinerUExtractRequest, MinerUExtractResponse, MinerUResultResponse
from services.task_manager import task_manager, TaskType, TaskStatus
from services.mineru_service import mineru_service
from utils.storage import storage

router = APIRouter(prefix="/mineru", tags=["MinerU提取"])

@router.post("/extract", response_model=MinerUExtractResponse)
async def start_extraction(request: MinerUExtractRequest, background_tasks: BackgroundTasks):
    file_path = storage.get_uploaded_file(request.file_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="文件不存在")

    task = task_manager.create_task(TaskType.MINERU, source_id=request.file_id)
    background_tasks.add_task(mineru_service.extract, file_path, task.task_id)

    return MinerUExtractResponse(
        task_id=task.task_id,
        file_id=request.file_id,
        status=task.status.value,
        created_at=task.created_at
    )

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return task.to_dict()

@router.get("/tasks/{task_id}/result", response_model=MinerUResultResponse)
async def get_extraction_result(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="任务未完成")

    data = None
    if task.result_file:
        data = storage.read_json(Path(task.result_file))

    return MinerUResultResponse(
        task_id=task_id,
        status=task.status.value,
        result_file=task.result_file,
        questions_count=len(data.get("questions", [])) if data and isinstance(data, dict) else 0,
        data=data
    )

@router.get("/results/{file_id}")
async def get_result_by_file(file_id: str):
    raw_json = storage.get_raw_json(file_id)
    if not raw_json:
        raise HTTPException(status_code=404, detail="结果不存在")

    data = storage.read_json(raw_json)
    return {
        "file_id": file_id,
        "result_file": str(raw_json),
        "data": data
    }

@router.post("/batch-extract")
async def batch_extract(request: dict, background_tasks: BackgroundTasks):
    file_ids = request.get("file_ids", [])
    tasks = []

    for file_id in file_ids:
        file_path = storage.get_uploaded_file(file_id)
        if file_path:
            task = task_manager.create_task(TaskType.MINERU, source_id=file_id)
            background_tasks.add_task(mineru_service.extract, file_path, task.task_id)
            tasks.append({"file_id": file_id, "task_id": task.task_id})

    return {
        "total": len(tasks),
        "tasks": tasks
    }
