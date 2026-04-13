from datetime import datetime
from typing import Optional, List
from services.database.connection import get_db_connection


def init_question_table():
    """初始化题目表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            question_id TEXT PRIMARY KEY,
            exam_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            title TEXT,
            content TEXT,
            answer TEXT,
            analysis TEXT,
            options TEXT,
            question_index INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (exam_id) REFERENCES exams(exam_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    conn.commit()
    conn.close()


def create_question(question_id: str, exam_id: str, user_id: str, title: str, content: str,
                    answer: str = None, analysis: str = None, options: str = None,
                    question_index: int = 0) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO questions (question_id, exam_id, user_id, title, content, answer, analysis, options, question_index, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (question_id, exam_id, user_id, title, content, answer, analysis, options, question_index, now, now)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def get_question_by_id(question_id: str, user_id: str = None) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM questions WHERE question_id = ? AND user_id = ?", (question_id, user_id))
    else:
        cursor.execute("SELECT * FROM questions WHERE question_id = ?", (question_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_questions_by_exam(exam_id: str, user_id: str = None) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute(
            "SELECT * FROM questions WHERE exam_id = ? AND user_id = ? ORDER BY question_index",
            (exam_id, user_id)
        )
    else:
        cursor.execute("SELECT * FROM questions WHERE exam_id = ? ORDER BY question_index", (exam_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_question(question_id: str, user_id: str, title: str = None, content: str = None,
                   answer: str = None, analysis: str = None, options: str = None) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []

    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if answer is not None:
        updates.append("answer = ?")
        params.append(answer)
    if analysis is not None:
        updates.append("analysis = ?")
        params.append(analysis)
    if options is not None:
        updates.append("options = ?")
        params.append(options)

    if not updates:
        return False

    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(question_id)
    params.append(user_id)

    cursor.execute(
        f"UPDATE questions SET {', '.join(updates)} WHERE question_id = ? AND user_id = ?",
        params
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def get_questions_count_by_exam(exam_id: str, user_id: str = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT COUNT(*) FROM questions WHERE exam_id = ? AND user_id = ?", (exam_id, user_id))
    else:
        cursor.execute("SELECT COUNT(*) FROM questions WHERE exam_id = ?", (exam_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count
