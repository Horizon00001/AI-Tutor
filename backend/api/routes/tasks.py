from fastapi import APIRouter, HTTPException
from typing import Optional

from api.models.schemas import TaskStatusResponse
from services.task_manager import task_manager, TaskType, TaskStatus

router = APIRouter(prefix="/tasks", tags=["任务管理"])

@router.get("")
async def list_tasks(
    task_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    type_filter = TaskType(task_type) if task_type else None
    status_filter = TaskStatus(status) if status else None

    tasks = task_manager.list_tasks(type_filter, status_filter)

    total = len(tasks)
    start = (page - 1) * limit
    end = start + limit

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "tasks": [t.to_dict() for t in tasks[start:end]]
    }

@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return TaskStatusResponse(
        task_id=task.task_id,
        task_type=task.task_type.value,
        status=task.status.value,
        progress=task.progress,
        current_step=task.current_step,
        error=task.error,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

@router.delete("/{task_id}")
async def delete_task(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task_manager.delete_task(task_id)
    return {"message": "任务已删除", "task_id": task_id}

@router.post("/{task_id}/retry")
async def retry_task(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != TaskStatus.FAILED:
        raise HTTPException(status_code=400, detail="只有失败的任务可以重试")

    task.update_status(TaskStatus.PENDING, progress=0, step="等待重试...")
    task.error = None

    return {"message": "任务已重置", "task_id": task_id, "status": "pending"}
