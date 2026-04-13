from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from api.routes.auth import get_current_user
from services.exam_service import (
    create_exam_record, get_exam_record, list_exams,
    get_exam_questions, update_question_record, remove_exam
)
from services.database import init_db

router = APIRouter(prefix="/exams", tags=["试卷管理"])


class CreateExamRequest(BaseModel):
    source: str
    cleaned_json_path: Optional[str] = None
    raw_json_path: Optional[str] = None


class UpdateQuestionRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    answer: Optional[str] = None
    analysis: Optional[str] = None
    options: Optional[dict] = None


@router.post("")
async def create_exam(request: CreateExamRequest, current_user: dict = Depends(get_current_user)):
    init_db()
    result = create_exam_record(
        user_id=current_user["user_id"],
        source=request.source,
        raw_json_path=request.raw_json_path,
        cleaned_json_path=request.cleaned_json_path
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    exam = get_exam_record(result["exam_id"], current_user["user_id"])
    return exam


@router.get("")
async def list_all_exams(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    init_db()
    result = list_exams(current_user["user_id"], page, limit)
    return result


@router.get("/{exam_id}")
async def get_exam(exam_id: str, current_user: dict = Depends(get_current_user)):
    init_db()
    exam = get_exam_record(exam_id, current_user["user_id"])

    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")

    return exam


@router.get("/{exam_id}/questions")
async def get_questions(exam_id: str, current_user: dict = Depends(get_current_user)):
    init_db()
    exam = get_exam_record(exam_id, current_user["user_id"])

    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")

    questions = get_exam_questions(exam_id, current_user["user_id"])

    return {
        "exam_id": exam_id,
        "source": exam["source"],
        "questions_count": len(questions),
        "questions": questions
    }


@router.put("/{exam_id}/questions/{question_id}")
async def update_question_endpoint(
    exam_id: str,
    question_id: str,
    request: UpdateQuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    init_db()
    exam = get_exam_record(exam_id, current_user["user_id"])

    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")

    result = update_question_record(
        question_id=question_id,
        user_id=current_user["user_id"],
        title=request.title,
        content=request.content,
        answer=request.answer,
        analysis=request.analysis,
        options=request.options
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.delete("/{exam_id}")
async def delete_exam_endpoint(exam_id: str, current_user: dict = Depends(get_current_user)):
    init_db()
    result = remove_exam(exam_id, current_user["user_id"])

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return {"message": "试卷删除成功"}
