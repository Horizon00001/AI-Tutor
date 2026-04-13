from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form, HTTPException
from datetime import datetime
from pathlib import Path
from typing import Optional

from api.models.schemas import PipelineFullResponse, PipelineStatusResponse
from services.task_manager import task_manager, TaskType, TaskStatus
from services.mineru_service import mineru_service
from services.deepseek_service import deepseek_service
from services.ppt_service import ppt_service
from services.exam_service import create_exam_record, add_questions_from_json
from services.database import init_db
from utils.file_handler import file_handler
from utils.storage import storage

router = APIRouter(prefix="/pipeline", tags=["完整管道"])

pipelines = {}

@router.post("/full", response_model=PipelineFullResponse)
async def full_pipeline(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    use_animation: bool = Form(True),
    title: Optional[str] = Form("试卷评讲"),
    user_id: str = Form("default_user")
):
    content = await file.read()

    is_valid, error_msg = file_handler.validate_file(file.filename, content)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    file_id = file_handler.generate_file_id()
    file_path = storage.save_uploaded_file(file_id, file.filename, content)

    pipeline_id = file_handler.generate_file_id()
    pipeline = {
        "pipeline_id": pipeline_id,
        "stages": {},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    pipelines[pipeline_id] = pipeline

    pipeline["stages"]["upload"] = {
        "file_id": file_id,
        "status": "completed"
    }

    mineru_task = task_manager.create_task(TaskType.MINERU, source_id=file_id)
    pipeline["stages"]["mineru"] = {
        "task_id": mineru_task.task_id,
        "status": "pending"
    }

    async def run_pipeline():
        try:
            pipeline["stages"]["mineru"]["status"] = "processing"
            result = await mineru_service.extract(file_path, mineru_task.task_id)

            if result:
                pipeline["stages"]["mineru"]["status"] = "completed"
                pipeline["stages"]["mineru"]["result_file"] = str(result)

                deepseek_task = task_manager.create_task(TaskType.DEEPSEEK, source_id=mineru_task.task_id)
                pipeline["stages"]["deepseek"] = {
                    "task_id": deepseek_task.task_id,
                    "status": "processing"
                }

                fixed_result = await deepseek_service.fix_json(result, deepseek_task.task_id)

                if fixed_result:
                    pipeline["stages"]["deepseek"]["status"] = "completed"
                    pipeline["stages"]["deepseek"]["result_file"] = str(fixed_result)

                    # 初始化数据库并创建试卷记录
                    init_db()
                    exam_result = create_exam_record(
                        user_id=user_id,
                        source=file.filename,
                        raw_json_path=str(result),
                        cleaned_json_path=str(fixed_result)
                    )

                    if exam_result["success"]:
                        pipeline["exam_id"] = exam_result["exam_id"]

                        # 提取题目存入 questions 表
                        add_questions_from_json(
                            exam_id=exam_result["exam_id"],
                            user_id=user_id,
                            json_file_path=str(fixed_result)
                        )

                    ppt_task = task_manager.create_task(TaskType.PPT, source_id=str(fixed_result))
                    pipeline["stages"]["ppt"] = {
                        "task_id": ppt_task.task_id,
                        "status": "processing"
                    }

                    ppt_result = await ppt_service.generate(fixed_result, use_animation, title, ppt_task.task_id)

                    if ppt_result:
                        pipeline["stages"]["ppt"]["status"] = "completed"
                        pipeline["stages"]["ppt"]["pptx_file"] = str(ppt_result)
                    else:
                        pipeline["stages"]["ppt"]["status"] = "failed"
                else:
                    pipeline["stages"]["deepseek"]["status"] = "failed"
            else:
                pipeline["stages"]["mineru"]["status"] = "failed"

        except Exception as e:
            print(f"Pipeline error: {e}")

    background_tasks.add_task(run_pipeline)

    return PipelineFullResponse(
        pipeline_id=pipeline_id,
        stages=pipeline["stages"],
        created_at=pipeline["created_at"]
    )

@router.get("/{pipeline_id}", response_model=PipelineStatusResponse)
async def get_pipeline_status(pipeline_id: str):
    pipeline = pipelines.get(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="管道不存在")

    stages = pipeline["stages"]
    all_completed = all(
        stage.get("status") == "completed"
        for stage in stages.values()
        if isinstance(stage, dict) and "status" in stage
    )

    return PipelineStatusResponse(
        pipeline_id=pipeline_id,
        stages=stages,
        all_completed=all_completed
    )

@router.post("/upload-and-extract")
async def upload_and_extract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    content = await file.read()

    is_valid, error_msg = file_handler.validate_file(file.filename, content)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    file_id = file_handler.generate_file_id()
    file_path = storage.save_uploaded_file(file_id, file.filename, content)

    task = task_manager.create_task(TaskType.MINERU, source_id=file_id)
    background_tasks.add_task(mineru_service.extract, file_path, task.task_id)

    return {
        "file_id": file_id,
        "task_id": task.task_id,
        "status": "processing"
    }

@router.post("/extract-and-fix")
async def extract_and_fix(request: dict, background_tasks: BackgroundTasks):
    mineru_task_id = request.get("mineru_task_id")
    mineru_task = task_manager.get_task(mineru_task_id)

    if not mineru_task or mineru_task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="MinerU任务未完成")

    if not mineru_task.result_file:
        raise HTTPException(status_code=400, detail="MinerU任务没有结果文件")

    task = task_manager.create_task(TaskType.DEEPSEEK, source_id=mineru_task_id)
    background_tasks.add_task(deepseek_service.fix_json, Path(mineru_task.result_file), task.task_id)

    return {
        "mineru_task_id": mineru_task_id,
        "deepseek_task_id": task.task_id,
        "status": "processing"
    }

@router.post("/fix-and-generate")
async def fix_and_generate(request: dict, background_tasks: BackgroundTasks):
    deepseek_task_id = request.get("deepseek_task_id")
    use_animation = request.get("use_animation", True)
    title = request.get("title", "试卷评讲")

    deepseek_task = task_manager.get_task(deepseek_task_id)

    if not deepseek_task or deepseek_task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="DeepSeek任务未完成")

    if not deepseek_task.result_file:
        raise HTTPException(status_code=400, detail="DeepSeek任务没有结果文件")

    task = task_manager.create_task(TaskType.PPT, source_id=deepseek_task_id)
    background_tasks.add_task(
        ppt_service.generate,
        Path(deepseek_task.result_file),
        use_animation,
        title,
        task.task_id
    )

    return {
        "deepseek_task_id": deepseek_task_id,
        "ppt_task_id": task.task_id,
        "status": "processing"
    }
