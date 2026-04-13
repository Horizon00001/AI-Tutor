from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from services.task_manager import task_manager, TaskType, TaskStatus
from utils.storage import storage

router = APIRouter(prefix="/download", tags=["文件下载"])

@router.get("/json/{task_id}")
async def download_json(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.task_type != TaskType.DEEPSEEK:
        raise HTTPException(status_code=400, detail="该任务不是DeepSeek修复任务")

    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="任务未完成")

    if not task.result_file or not Path(task.result_file).exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=task.result_file,
        filename=Path(task.result_file).name,
        media_type="application/json"
    )

@router.get("/ppt/{task_id}")
async def download_ppt(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.task_type != TaskType.PPT:
        raise HTTPException(status_code=400, detail="该任务不是PPT生成任务")

    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="任务未完成")

    if not task.result_file or not Path(task.result_file).exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=task.result_file,
        filename=Path(task.result_file).name,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

@router.get("/raw/{task_id}")
async def download_raw_json(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.task_type != TaskType.MINERU:
        raise HTTPException(status_code=400, detail="该任务不是MinerU提取任务")

    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="任务未完成")

    if not task.result_file or not Path(task.result_file).exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=task.result_file,
        filename=Path(task.result_file).name,
        media_type="application/json"
    )
