#!/usr/bin/env python3
"""
简单测试自动存库功能 - 直接调用服务函数
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from pathlib import Path
from services.database import init_db
from services.exam_service import create_exam_record, add_questions_from_json

def test_auto_save():
    print("="*50)
    print("测试: 自动存库功能")
    print("="*50)

    # 初始化数据库
    init_db()
    print("✓ 数据库初始化完成")

    # 找一个测试用的JSON文件
    json_files = list(Path("output/processed_json").glob("*_cleaned.json"))
    if not json_files:
        print("✗ 没有找到processed_json文件")
        return False

    test_json = json_files[0]
    print(f"ℹ 使用测试文件: {test_json.name}")

    # 1. 创建试卷记录
    user_id = "test_user_123"
    source = "测试试卷"
    raw_json_path = "output/raw_json/test.json"
    cleaned_json_path = str(test_json)

    exam_result = create_exam_record(
        user_id=user_id,
        source=source,
        raw_json_path=raw_json_path,
        cleaned_json_path=cleaned_json_path
    )

    if not exam_result["success"]:
        print(f"✗ 创建试卷失败: {exam_result.get('error')}")
        return False

    exam_id = exam_result["exam_id"]
    print(f"✓ 试卷创建成功: {exam_id}")

    # 2. 提取题目到数据库
    result = add_questions_from_json(
        exam_id=exam_id,
        user_id=user_id,
        json_file_path=cleaned_json_path
    )

    if not result["success"]:
        print(f"✗ 添加题目失败: {result.get('error')}")
        return False

    print(f"✓ 题目添加成功: {result['added_count']}/{result['total_count']} 道")

    # 3. 验证数据库
    import sqlite3
    conn = sqlite3.connect('data/data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM questions WHERE exam_id = ?", (exam_id,))
    count = cursor.fetchone()[0]
    print(f"✓ 数据库验证: 该试卷共有 {count} 道题目")

    cursor.execute("SELECT title, content FROM questions WHERE exam_id = ? LIMIT 2", (exam_id,))
    questions = cursor.fetchall()
    for i, (title, content) in enumerate(questions):
        print(f"  [{i+1}] {title}: {content[:60]}...")

    conn.close()

    print("\n" + "="*50)
    print("✓ 自动存库功能测试通过!")
    print("="*50)
    return True

if __name__ == "__main__":
    test_auto_save()
