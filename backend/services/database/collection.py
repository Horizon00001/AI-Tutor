import sqlite3
from datetime import datetime
from typing import Optional, List
from services.database.connection import get_db_connection


def init_collection_tables():
    """初始化收藏相关表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher_folders (
            folder_id TEXT PRIMARY KEY,
            teacher_id TEXT NOT NULL,
            name TEXT NOT NULL,
            parent_id TEXT,
            color TEXT DEFAULT '#1890ff',
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES teacher_folders(folder_id),
            FOREIGN KEY (teacher_id) REFERENCES users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher_collections (
            collection_id TEXT PRIMARY KEY,
            teacher_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            folder_id TEXT,
            title TEXT,
            content TEXT,
            answer TEXT,
            analysis TEXT,
            tags TEXT,
            difficulty_note TEXT,
            teach_note TEXT,
            common_errors TEXT,
            teach_points TEXT,
            use_count INTEGER DEFAULT 0,
            last_used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(user_id),
            FOREIGN KEY (question_id) REFERENCES questions(question_id),
            FOREIGN KEY (folder_id) REFERENCES teacher_folders(folder_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collection_tags (
            tag_id TEXT PRIMARY KEY,
            teacher_id TEXT NOT NULL,
            tag_name TEXT NOT NULL,
            color TEXT DEFAULT '#52c41a',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(user_id),
            UNIQUE(teacher_id, tag_name)
        )
    """)

    conn.commit()
    conn.close()


# ==================== 收藏文件夹操作 ====================

def create_teacher_folder(folder_id: str, teacher_id: str, name: str, parent_id: str = None, color: str = None) -> bool:
    """创建收藏文件夹"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        now = datetime.now().isoformat()
        cursor.execute(
            """INSERT INTO teacher_folders (folder_id, teacher_id, name, parent_id, color, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (folder_id, teacher_id, name, parent_id, color or '#1890ff', now, now)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_teacher_folders(teacher_id: str) -> List[dict]:
    """获取教师的所有文件夹"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM teacher_folders WHERE teacher_id = ? ORDER BY sort_order, created_at",
        (teacher_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_folder_by_id(folder_id: str, teacher_id: str = None) -> Optional[dict]:
    """获取文件夹详情"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if teacher_id:
        cursor.execute(
            "SELECT * FROM teacher_folders WHERE folder_id = ? AND teacher_id = ?",
            (folder_id, teacher_id)
        )
    else:
        cursor.execute("SELECT * FROM teacher_folders WHERE folder_id = ?", (folder_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def update_teacher_folder(folder_id: str, teacher_id: str, name: str = None, color: str = None, parent_id: str = None) -> bool:
    """更新文件夹"""
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []

    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if color is not None:
        updates.append("color = ?")
        params.append(color)
    if parent_id is not None:
        updates.append("parent_id = ?")
        params.append(parent_id)

    if not updates:
        return False

    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(folder_id)
    params.append(teacher_id)

    cursor.execute(
        f"UPDATE teacher_folders SET {', '.join(updates)} WHERE folder_id = ? AND teacher_id = ?",
        params
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def delete_teacher_folder(folder_id: str, teacher_id: str) -> bool:
    """删除文件夹"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM teacher_folders WHERE folder_id = ? AND teacher_id = ?",
        (folder_id, teacher_id)
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def move_folder_to_root(folder_id: str, teacher_id: str) -> bool:
    """将子文件夹移动到根目录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE teacher_folders SET parent_id = NULL, updated_at = ? WHERE parent_id = ? AND teacher_id = ?",
        (datetime.now().isoformat(), folder_id, teacher_id)
    )
    conn.commit()
    conn.close()
    return True


# ==================== 题目收藏操作 ====================

def create_collection(collection_id: str, teacher_id: str, question_id: str, folder_id: str = None,
                     title: str = None, content: str = None, answer: str = None, analysis: str = None,
                     tags: str = None, difficulty_note: str = None, teach_note: str = None,
                     common_errors: str = None, teach_points: str = None) -> bool:
    """创建题目收藏"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        now = datetime.now().isoformat()
        cursor.execute(
            """INSERT INTO teacher_collections
               (collection_id, teacher_id, question_id, folder_id, title, content, answer, analysis,
                tags, difficulty_note, teach_note, common_errors, teach_points, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (collection_id, teacher_id, question_id, folder_id, title, content, answer, analysis,
             tags, difficulty_note, teach_note, common_errors, teach_points, now, now)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_collection_by_id(collection_id: str, teacher_id: str = None) -> Optional[dict]:
    """获取收藏详情"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if teacher_id:
        cursor.execute(
            """SELECT c.*, f.name as folder_name
               FROM teacher_collections c
               LEFT JOIN teacher_folders f ON c.folder_id = f.folder_id
               WHERE c.collection_id = ? AND c.teacher_id = ?""",
            (collection_id, teacher_id)
        )
    else:
        cursor.execute(
            """SELECT c.*, f.name as folder_name
               FROM teacher_collections c
               LEFT JOIN teacher_folders f ON c.folder_id = f.folder_id
               WHERE c.collection_id = ?""",
            (collection_id,)
        )
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_collections_by_teacher(teacher_id: str, folder_id: str = None, tag: str = None,
                               keyword: str = None, page: int = 1, limit: int = 20) -> tuple:
    """获取教师收藏列表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    where_clauses = ["c.teacher_id = ?"]
    params = [teacher_id]

    if folder_id:
        where_clauses.append("c.folder_id = ?")
        params.append(folder_id)

    if tag:
        where_clauses.append("c.tags LIKE ?")
        params.append(f'%"{tag}"%')

    if keyword:
        where_clauses.append("(c.title LIKE ? OR c.content LIKE ? OR c.teach_note LIKE ?)")
        params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])

    where_sql = " AND ".join(where_clauses)

    cursor.execute(f"SELECT COUNT(*) FROM teacher_collections c WHERE {where_sql}", params)
    total = cursor.fetchone()[0]

    offset = (page - 1) * limit
    cursor.execute(
        f"""SELECT c.*, f.name as folder_name
            FROM teacher_collections c
            LEFT JOIN teacher_folders f ON c.folder_id = f.folder_id
            WHERE {where_sql}
            ORDER BY c.created_at DESC
            LIMIT ? OFFSET ?""",
        params + [limit, offset]
    )
    rows = cursor.fetchall()
    conn.close()

    collections = [dict(row) for row in rows]
    return total, collections


def update_collection(collection_id: str, teacher_id: str, **kwargs) -> bool:
    """更新收藏信息"""
    conn = get_db_connection()
    cursor = conn.cursor()

    allowed_fields = ['folder_id', 'tags', 'difficulty_note', 'teach_note',
                      'common_errors', 'teach_points']
    updates = []
    params = []

    for field, value in kwargs.items():
        if field in allowed_fields and value is not None:
            updates.append(f"{field} = ?")
            params.append(value)

    if not updates:
        return False

    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(collection_id)
    params.append(teacher_id)

    cursor.execute(
        f"UPDATE teacher_collections SET {', '.join(updates)} WHERE collection_id = ? AND teacher_id = ?",
        params
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def delete_collection(collection_id: str, teacher_id: str) -> bool:
    """删除收藏"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM teacher_collections WHERE collection_id = ? AND teacher_id = ?",
        (collection_id, teacher_id)
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def record_collection_usage(collection_id: str, teacher_id: str) -> bool:
    """记录收藏使用次数"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE teacher_collections
           SET use_count = use_count + 1, last_used_at = ?
           WHERE collection_id = ? AND teacher_id = ?""",
        (datetime.now().isoformat(), collection_id, teacher_id)
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def move_collections_to_folder(collection_ids: List[str], folder_id: str, teacher_id: str) -> int:
    """批量移动收藏到文件夹"""
    conn = get_db_connection()
    cursor = conn.cursor()

    placeholders = ','.join(['?' for _ in collection_ids])
    cursor.execute(
        f"""UPDATE teacher_collections
           SET folder_id = ?, updated_at = ?
           WHERE collection_id IN ({placeholders}) AND teacher_id = ?""",
        [folder_id, datetime.now().isoformat()] + collection_ids + [teacher_id]
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected


def batch_delete_collections(collection_ids: List[str], teacher_id: str) -> int:
    """批量删除收藏"""
    conn = get_db_connection()
    cursor = conn.cursor()

    placeholders = ','.join(['?' for _ in collection_ids])
    cursor.execute(
        f"DELETE FROM teacher_collections WHERE collection_id IN ({placeholders}) AND teacher_id = ?",
        collection_ids + [teacher_id]
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected


def is_question_collected(teacher_id: str, question_id: str) -> bool:
    """检查题目是否已收藏"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM teacher_collections WHERE teacher_id = ? AND question_id = ? LIMIT 1",
        (teacher_id, question_id)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


# ==================== 收藏标签操作 ====================

def create_collection_tag(tag_id: str, teacher_id: str, tag_name: str, color: str = None) -> bool:
    """创建收藏标签"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO collection_tags (tag_id, teacher_id, tag_name, color) VALUES (?, ?, ?, ?)",
            (tag_id, teacher_id, tag_name, color or '#52c41a')
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_collection_tags(teacher_id: str) -> List[dict]:
    """获取教师的所有标签"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT t.*, COUNT(c.collection_id) as use_count
           FROM collection_tags t
           LEFT JOIN teacher_collections c ON c.tags LIKE '%' || t.tag_name || '%' AND c.teacher_id = t.teacher_id
           WHERE t.teacher_id = ?
           GROUP BY t.tag_id
           ORDER BY use_count DESC, t.created_at""",
        (teacher_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_tag_by_id(tag_id: str, teacher_id: str = None) -> Optional[dict]:
    """获取标签详情"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if teacher_id:
        cursor.execute(
            "SELECT * FROM collection_tags WHERE tag_id = ? AND teacher_id = ?",
            (tag_id, teacher_id)
        )
    else:
        cursor.execute("SELECT * FROM collection_tags WHERE tag_id = ?", (tag_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def update_collection_tag(tag_id: str, teacher_id: str, tag_name: str = None, color: str = None) -> bool:
    """更新标签"""
    conn = get_db_connection()
    cursor = conn.cursor()

    updates = []
    params = []

    if tag_name is not None:
        updates.append("tag_name = ?")
        params.append(tag_name)
    if color is not None:
        updates.append("color = ?")
        params.append(color)

    if not updates:
        return False

    params.append(tag_id)
    params.append(teacher_id)

    try:
        cursor.execute(
            f"UPDATE collection_tags SET {', '.join(updates)} WHERE tag_id = ? AND teacher_id = ?",
            params
        )
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except sqlite3.IntegrityError:
        conn.close()
        return False


def delete_collection_tag(tag_id: str, teacher_id: str) -> bool:
    """删除标签"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM collection_tags WHERE tag_id = ? AND teacher_id = ?",
        (tag_id, teacher_id)
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success
