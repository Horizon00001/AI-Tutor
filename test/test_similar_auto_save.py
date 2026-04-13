#!/usr/bin/env python3
"""
测试相似题目自动存库功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.database import init_db
from services.exam_service import save_similar_questions

def test_similar_auto_save():
    print("="*50)
    print("测试: 相似题目自动存库功能")
    print("="*50)

    # 初始化数据库
    init_db()
    print("✓ 数据库初始化完成")

    # 模拟相似题目数据
    source_question_id = "test_question_123"
    exam_id = "test_exam_456"
    user_id = "test_user_789"

    similar_questions = [
        {
            "title": "相似题1",
            "content": "这是一道相似题目的内容",
            "answer": "答案是A",
            "analysis": "解析内容",
            "difficulty": "same"
        },
        {
            "title": "相似题2",
            "content": "这是另一道相似题目的内容",
            "answer": "答案是B",
            "analysis": "解析内容2",
            "difficulty": "easier"
        }
    ]

    # 保存相似题目到数据库
    result = save_similar_questions(
        source_question_id=source_question_id,
        exam_id=exam_id,
        user_id=user_id,
        similar_questions=similar_questions
    )

    if not result["success"]:
        print(f"✗ 保存相似题目失败: {result.get('error')}")
        return False

    print(f"✓ 相似题目保存成功: {result['saved_count']}/{len(similar_questions)} 道")

    # 验证数据库
    import sqlite3
    conn = sqlite3.connect('data/data.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM similar_questions WHERE source_question_id = ?",
        (source_question_id,)
    )
    count = cursor.fetchone()[0]
    print(f"✓ 数据库验证: 该原题共有 {count} 道相似题目")

    cursor.execute(
        "SELECT title, content, difficulty FROM similar_questions WHERE source_question_id = ? LIMIT 2",
        (source_question_id,)
    )
    questions = cursor.fetchall()
    for i, (title, content, difficulty) in enumerate(questions):
        print(f"  [{i+1}] {title} (难度: {difficulty}): {content[:40]}...")

    conn.close()

    print("\n" + "="*50)
    print("✓ 相似题目自动存库功能测试通过!")
    print("="*50)
    return True

if __name__ == "__main__":
    test_similar_auto_save()
