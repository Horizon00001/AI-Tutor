from fastapi import APIRouter, BackgroundTasks, HTTPException
from datetime import datetime
from typing import List

from api.models.schemas import (
    GenerateSimilarRequest, GenerateSimilarResponse,
    SimilarQuestionResultResponse, BatchGenerateSimilarRequest, BatchGenerateSimilarResponse
)
from services.task_manager import task_manager, TaskType, TaskStatus
from services.deepseek_service import deepseek_service
from services.similar_question_service import similar_question_service

router = APIRouter(prefix="/questions", tags=["相似题生成"])

@router.post("/{task_id}/{question_index}/generate-similar", response_model=GenerateSimilarResponse)
async def generate_similar_question(
    task_id: str,
    question_index: int,
    request: GenerateSimilarRequest,
    background_tasks: BackgroundTasks
):
    questions = deepseek_service.get_questions_from_task(task_id)
    if not questions:
        raise HTTPException(status_code=404, detail="未找到题目数据，请确保DeepSeek任务已完成")

    if question_index < 0 or question_index >= len(questions):
        raise HTTPException(status_code=400, detail=f"题目索引超出范围，有效范围: 0-{len(questions)-1}")

    source_question = questions[question_index]

    task = task_manager.create_task(TaskType.SIMILAR_QUESTION, source_id=task_id)
    task.data = {
        "source_question": source_question,
        "question_index": question_index,
        "count": request.count,
        "difficulty_adjustment": request.difficulty_adjustment
    }

    background_tasks.add_task(
        similar_question_service.generate_similar,
        source_question,
        source_question.get('question_id', ''),  # 原题ID
        request.exam_id,
        request.user_id,
        request.count,
        request.difficulty_adjustment,
        request.preserve_knowledge_points,
        task.task_id
    )

    return GenerateSimilarResponse(
        task_id=task.task_id,
        status=task.status.value,
        source_question=source_question,
        generation_config={
            "count": request.count,
            "difficulty_adjustment": request.difficulty_adjustment
        },
        created_at=task.created_at
    )

@router.get("/similar-tasks/{task_id}")
async def get_similar_task_status(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return task.to_dict()

@router.get("/similar-tasks/{task_id}/result", response_model=SimilarQuestionResultResponse)
async def get_similar_question_result(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="任务未完成")

    return SimilarQuestionResultResponse(
        task_id=task_id,
        status=task.status.value,
        source_question=task.data.get("source_question", {}),
        similar_questions=task.data.get("similar_questions", []),
        generated_count=task.data.get("generated_count", 0),
        created_at=task.created_at,
        completed_at=task.completed_at
    )

@router.post("/{task_id}/batch-generate", response_model=BatchGenerateSimilarResponse)
async def batch_generate_similar(
    task_id: str,
    request: BatchGenerateSimilarRequest,
    background_tasks: BackgroundTasks
):
    questions = deepseek_service.get_questions_from_task(task_id)
    if not questions:
        raise HTTPException(status_code=404, detail="未找到题目数据")

    tasks = []
    for idx in request.question_indices:
        if 0 <= idx < len(questions):
            source_question = questions[idx]
            task = task_manager.create_task(TaskType.SIMILAR_QUESTION, source_id=task_id)
            task.data = {
                "source_question": source_question,
                "question_index": idx,
                "count": request.count_per_question,
                "difficulty_adjustment": request.difficulty_adjustment
            }

            background_tasks.add_task(
                similar_question_service.generate_similar,
                source_question,
                source_question.get('question_id', ''),  # 原题ID
                request.exam_id,
                request.user_id,
                request.count_per_question,
                request.difficulty_adjustment,
                True,
                task.task_id
            )

            tasks.append({"question_index": idx, "similar_task_id": task.task_id})

    return BatchGenerateSimilarResponse(
        batch_task_id=task_manager.create_task(TaskType.SIMILAR_QUESTION).task_id,
        tasks=tasks,
        total_questions=len(tasks) * request.count_per_question,
        created_at=datetime.now()
    )
