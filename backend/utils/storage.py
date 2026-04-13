import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from utils.config import UPLOAD_DIR, RAW_JSON_DIR, PROCESSED_JSON_DIR, PPT_DIR, SIMILAR_QUESTIONS_DIR


class Storage:
    """文件存储工具"""

    @staticmethod
    def save_json(data: Any, file_path: Path) -> bool:
        """保存JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @staticmethod
    def load_json(file_path: Path) -> Optional[Any]:
        """加载JSON文件"""
        try:
            if not file_path.exists():
                return None
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    @staticmethod
    def save_uploaded_file(file_id: str, filename: str, content: bytes) -> Path:
        """保存上传的文件，返回文件路径"""
        ext = Path(filename).suffix.lower()
        dest_path = UPLOAD_DIR / f"{file_id}{ext}"
        with open(dest_path, 'wb') as f:
            f.write(content)
        return dest_path

    @staticmethod
    def get_raw_json_path(task_id: str, filename: str) -> Path:
        """获取原始JSON路径"""
        return RAW_JSON_DIR / filename / f"{task_id}_content_list.json"

    @staticmethod
    def get_processed_json_path(task_id: str, filename: str) -> Path:
        """获取处理后JSON路径"""
        return PROCESSED_JSON_DIR / f"{task_id}_content_list_cleaned.json"

    @staticmethod
    def get_ppt_path(task_id: str, filename: str) -> Path:
        """获取PPT路径"""
        return PPT_DIR / f"{task_id}_content_list_cleaned_fixed.pptx"

    @staticmethod
    def get_similar_questions_path(question_id: str) -> Path:
        """获取相似题JSON路径"""
        return SIMILAR_QUESTIONS_DIR / f"{question_id}_similar_questions.json"

    @staticmethod
    def save_similar_questions(task_id: str, source_question: dict, similar_questions: list) -> Path:
        """保存相似题结果"""
        data = {
            "task_id": task_id,
            "source_question": source_question,
            "similar_questions": similar_questions,
            "created_at": datetime.now().isoformat()
        }
        file_path = SIMILAR_QUESTIONS_DIR / f"{task_id}_similar_questions.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path


storage = Storage()
