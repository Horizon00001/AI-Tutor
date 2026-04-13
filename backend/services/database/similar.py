from datetime import datetime
from typing import List
from services.database.connection import get_db_connection


def init_similar_table():
    """初始化相似题表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS similar_questions (
            similar_id TEXT PRIMARY KEY,
            source_question_id TEXT NOT NULL,
            exam_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            title TEXT,
            content TEXT,
            answer TEXT,
            analysis TEXT,
            difficulty TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_question_id) REFERENCES questions(question_id),
            FOREIGN KEY (exam_id) REFERENCES exams(exam_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    conn.commit()
    conn.close()


def create_similar_question(similar_id: str, source_question_id: str, exam_id: str, user_id: str,
                           title: str, content: str, answer: str = None, analysis: str = None,
                           difficulty: str = None) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO similar_questions (similar_id, source_question_id, exam_id, user_id, title, content, answer, analysis, difficulty, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (similar_id, source_question_id, exam_id, user_id, title, content, answer, analysis, difficulty, datetime.now().isoformat())
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def get_similar_questions_by_source(source_question_id: str, user_id: str = None) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute(
            "SELECT * FROM similar_questions WHERE source_question_id = ? AND user_id = ? ORDER BY created_at DESC",
            (source_question_id, user_id)
        )
    else:
        cursor.execute("SELECT * FROM similar_questions WHERE source_question_id = ? ORDER BY created_at DESC",
                       (source_question_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_similar_questions_by_exam(exam_id: str, user_id: str = None) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute(
            "SELECT * FROM similar_questions WHERE exam_id = ? AND user_id = ? ORDER BY created_at DESC",
            (exam_id, user_id)
        )
    else:
        cursor.execute("SELECT * FROM similar_questions WHERE exam_id = ? ORDER BY created_at DESC", (exam_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
