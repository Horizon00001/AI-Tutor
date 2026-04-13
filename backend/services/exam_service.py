import uuid
import json
from pathlib import Path
from typing import Optional, List, Dict
from services.database import (
    create_exam, get_exam_by_id, list_user_exams, create_question,
    get_questions_by_exam, get_question_by_id, update_question, delete_exam,
    get_questions_count_by_exam, create_similar_question,
    get_similar_questions_by_source, get_similar_questions_by_exam
)


def create_exam_record(user_id: str, source: str, raw_json_path: str = None, cleaned_json_path: str = None) -> Dict:
    exam_id = str(uuid.uuid4())
    success = create_exam(exam_id, user_id, source, raw_json_path, cleaned_json_path)
    if not success:
        return {"success": False, "error": "创建试卷失败"}
    return {
        "success": True,
        "exam_id": exam_id,
        "source": source,
        "created_at": None
    }


def get_exam_record(exam_id: str, user_id: str = None) -> Optional[Dict]:
    exam = get_exam_by_id(exam_id, user_id)
    if not exam:
        return None

    questions_count = get_questions_count_by_exam(exam_id, user_id)

    return {
        "exam_id": exam["exam_id"],
        "user_id": exam["user_id"],
        "source": exam["source"],
        "raw_json_path": exam["raw_json_path"],
        "cleaned_json_path": exam["cleaned_json_path"],
        "questions_count": questions_count,
        "created_at": exam["created_at"],
        "updated_at": exam["updated_at"]
    }


def list_exams(user_id: str, page: int = 1, limit: int = 20) -> Dict:
    total, exams = list_user_exams(user_id, page, limit)

    result_exams = []
    for exam in exams:
        questions_count = get_questions_count_by_exam(exam["exam_id"], user_id)
        result_exams.append({
            "exam_id": exam["exam_id"],
            "source": exam["source"],
            "questions_count": questions_count,
            "created_at": exam["created_at"]
        })

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "exams": result_exams
    }


def add_questions_from_json(exam_id: str, user_id: str, json_file_path: str) -> Dict:
    file_path = Path(json_file_path)
    if not file_path.exists():
        return {"success": False, "error": "JSON文件不存在"}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
    except json.JSONDecodeError:
        return {"success": False, "error": "JSON文件格式错误"}

    if not isinstance(questions_data, list):
        questions_data = [questions_data]

    added_count = 0
    for idx, q in enumerate(questions_data):
        question_id = str(uuid.uuid4())

        options_json = None
        if "options" in q and isinstance(q["options"], (dict, list)):
            options_json = json.dumps(q["options"], ensure_ascii=False)

        success = create_question(
            question_id=question_id,
            exam_id=exam_id,
            user_id=user_id,
            title=q.get("title", str(idx + 1)),
            content=q.get("content", ""),
            answer=q.get("answer"),
            analysis=q.get("analysis"),
            options=options_json,
            question_index=idx
        )
        if success:
            added_count += 1

    return {
        "success": True,
        "added_count": added_count,
        "total_count": len(questions_data)
    }


def add_questions_to_exam(exam_id: str, user_id: str, questions: List[Dict]) -> Dict:
    added_count = 0
    for idx, q in enumerate(questions):
        question_id = str(uuid.uuid4())

        options_json = None
        if "options" in q and isinstance(q["options"], (dict, list)):
            options_json = json.dumps(q["options"], ensure_ascii=False)

        success = create_question(
            question_id=question_id,
            exam_id=exam_id,
            user_id=user_id,
            title=q.get("title", str(idx + 1)),
            content=q.get("content", ""),
            answer=q.get("answer"),
            analysis=q.get("analysis"),
            options=options_json,
            question_index=idx
        )
        if success:
            added_count += 1

    return {
        "success": True,
        "added_count": added_count
    }


def get_exam_questions(exam_id: str, user_id: str = None) -> List[Dict]:
    questions = get_questions_by_exam(exam_id, user_id)

    result = []
    for q in questions:
        options = None
        if q.get("options"):
            try:
                options = json.loads(q["options"])
            except json.JSONDecodeError:
                options = q["options"]

        result.append({
            "question_id": q["question_id"],
            "exam_id": q["exam_id"],
            "title": q["title"],
            "content": q["content"],
            "answer": q["answer"],
            "analysis": q["analysis"],
            "options": options,
            "question_index": q["question_index"],
            "created_at": q["created_at"],
            "updated_at": q["updated_at"]
        })

    return result


def update_question_record(question_id: str, user_id: str, title: str = None,
                           content: str = None, answer: str = None,
                           analysis: str = None, options: dict = None) -> Dict:
    options_json = None
    if options is not None:
        options_json = json.dumps(options, ensure_ascii=False)

    success = update_question(question_id, user_id, title, content, answer, analysis, options_json)

    if not success:
        return {"success": False, "error": "更新题目失败或题目不存在"}

    updated = get_question_by_id(question_id, user_id)
    return {
        "success": True,
        "question": {
            "question_id": updated["question_id"],
            "title": updated["title"],
            "content": updated["content"],
            "answer": updated["answer"],
            "analysis": updated["analysis"],
            "updated_at": updated["updated_at"]
        }
    }


def remove_exam(exam_id: str, user_id: str) -> Dict:
    exam = get_exam_by_id(exam_id, user_id)
    if not exam:
        return {"success": False, "error": "试卷不存在"}

    success = delete_exam(exam_id, user_id)
    if not success:
        return {"success": False, "error": "删除试卷失败"}

    return {"success": True}


def save_similar_questions(source_question_id: str, exam_id: str, user_id: str,
                          similar_questions: List[Dict]) -> Dict:
    saved_count = 0
    saved_questions = []

    for sq in similar_questions:
        similar_id = str(uuid.uuid4())
        success = create_similar_question(
            similar_id=similar_id,
            source_question_id=source_question_id,
            exam_id=exam_id,
            user_id=user_id,
            title=sq.get("title", ""),
            content=sq.get("content", ""),
            answer=sq.get("answer"),
            analysis=sq.get("analysis"),
            difficulty=sq.get("difficulty", "same")
        )
        if success:
            saved_count += 1
            saved_questions.append({
                "similar_id": similar_id,
                "title": sq.get("title", ""),
                "content": sq.get("content", ""),
                "answer": sq.get("answer"),
                "analysis": sq.get("analysis"),
                "difficulty": sq.get("difficulty", "same")
            })

    return {
        "success": True,
        "saved_count": saved_count,
        "similar_questions": saved_questions
    }


def get_question_similar_questions(source_question_id: str, user_id: str = None) -> List[Dict]:
    similar = get_similar_questions_by_source(source_question_id, user_id)
    return similar


def get_exam_all_similar_questions(exam_id: str, user_id: str = None) -> List[Dict]:
    similar = get_similar_questions_by_exam(exam_id, user_id)
    return similar
