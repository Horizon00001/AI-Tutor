from datetime import datetime
from typing import Optional, List, Tuple
from services.database.connection import get_db_connection


def init_exam_table():
    """初始化试卷表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            exam_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            source TEXT,
            raw_json_path TEXT,
            cleaned_json_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    conn.commit()
    conn.close()


def create_exam(exam_id: str, user_id: str, source: str, raw_json_path: str = None, cleaned_json_path: str = None) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO exams (exam_id, user_id, source, raw_json_path, cleaned_json_path, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (exam_id, user_id, source, raw_json_path, cleaned_json_path, now, now)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def get_exam_by_id(exam_id: str, user_id: str = None) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM exams WHERE exam_id = ? AND user_id = ?", (exam_id, user_id))
    else:
        cursor.execute("SELECT * FROM exams WHERE exam_id = ?", (exam_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def list_user_exams(user_id: str, page: int = 1, limit: int = 20) -> Tuple[int, List[dict]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    offset = (page - 1) * limit

    cursor.execute("SELECT COUNT(*) FROM exams WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT * FROM exams WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (user_id, limit, offset)
    )
    rows = cursor.fetchall()
    conn.close()

    exams = [dict(row) for row in rows]
    return total, exams


def delete_exam(exam_id: str, user_id: str) -> bool:
    """删除试卷及级联删除关联数据（题目、相似题、收藏）"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. 获取该试卷下的所有题目ID（用于删除关联收藏）
    cursor.execute("SELECT question_id FROM questions WHERE exam_id = ? AND user_id = ?", (exam_id, user_id))
    question_ids = [row[0] for row in cursor.fetchall()]

    # 2. 删除关联的收藏（通过 question_id）
    if question_ids:
        placeholders = ','.join(['?' for _ in question_ids])
        cursor.execute(
            f"DELETE FROM teacher_collections WHERE question_id IN ({placeholders}) AND teacher_id = ?",
            question_ids + [user_id]
        )

    # 3. 删除相似题
    cursor.execute("DELETE FROM similar_questions WHERE exam_id = ? AND user_id = ?", (exam_id, user_id))

    # 4. 删除题目
    cursor.execute("DELETE FROM questions WHERE exam_id = ? AND user_id = ?", (exam_id, user_id))

    # 5. 删除试卷
    cursor.execute("DELETE FROM exams WHERE exam_id = ? AND user_id = ?", (exam_id, user_id))

    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success
