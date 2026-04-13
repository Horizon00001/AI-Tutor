from datetime import timedelta
from typing import List
from services.database.connection import get_db_connection


def get_collection_stats(teacher_id: str) -> dict:
    """获取收藏统计信息"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 总收藏数
    cursor.execute(
        "SELECT COUNT(*) FROM teacher_collections WHERE teacher_id = ?",
        (teacher_id,)
    )
    total_count = cursor.fetchone()[0]

    # 文件夹数
    cursor.execute(
        "SELECT COUNT(*) FROM teacher_folders WHERE teacher_id = ?",
        (teacher_id,)
    )
    folder_count = cursor.fetchone()[0]

    # 标签数
    cursor.execute(
        "SELECT COUNT(*) FROM collection_tags WHERE teacher_id = ?",
        (teacher_id,)
    )
    tag_count = cursor.fetchone()[0]

    # 本周新增
    from datetime import datetime
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    cursor.execute(
        "SELECT COUNT(*) FROM teacher_collections WHERE teacher_id = ? AND created_at > ?",
        (teacher_id, week_ago)
    )
    this_week_count = cursor.fetchone()[0]

    # 最常用标签
    cursor.execute(
        """SELECT t.tag_name, t.color, COUNT(c.collection_id) as use_count
           FROM collection_tags t
           LEFT JOIN teacher_collections c ON c.tags LIKE '%' || t.tag_name || '%' AND c.teacher_id = t.teacher_id
           WHERE t.teacher_id = ?
           GROUP BY t.tag_id
           ORDER BY use_count DESC
           LIMIT 5""",
        (teacher_id,)
    )
    most_used_tags = [dict(row) for row in cursor.fetchall()]

    # 最近收藏
    cursor.execute(
        """SELECT collection_id, title, created_at
           FROM teacher_collections
           WHERE teacher_id = ?
           ORDER BY created_at DESC
           LIMIT 5""",
        (teacher_id,)
    )
    recent_collections = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "total_count": total_count,
        "folder_count": folder_count,
        "tag_count": tag_count,
        "this_week_count": this_week_count,
        "most_used_tags": most_used_tags,
        "recent_collections": recent_collections
    }
