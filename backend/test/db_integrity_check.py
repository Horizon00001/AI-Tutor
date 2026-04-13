#!/usr/bin/env python3
"""
数据库完整性检查和清理工具
用于检查并清理孤立的脏数据（关联到不存在记录的条目）
"""

import sqlite3
from datetime import datetime
import sys


def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect('data/data.db')


def check_integrity():
    """检查数据库完整性"""
    print("=" * 60)
    print("数据库完整性检查")
    print(f"执行时间: {datetime.now()}")
    print("=" * 60)
    print()

    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查 questions 表中的孤立记录
    print("[1] 检查 questions 表...")
    cursor.execute('''
        SELECT COUNT(*) FROM questions q
        WHERE q.exam_id NOT IN (SELECT exam_id FROM exams)
    ''')
    orphan_questions = cursor.fetchone()[0]
    
    if orphan_questions > 0:
        print(f"    ❌ 发现 {orphan_questions} 条孤立记录（exam_id 不存在）")
        cursor.execute('''
            SELECT question_id, exam_id, title, created_at
            FROM questions q
            WHERE q.exam_id NOT IN (SELECT exam_id FROM exams)
            LIMIT 5
        ''')
        for row in cursor.fetchall():
            print(f"      - {row[0][:20]}... (exam_id: {row[1][:20]}...)")
    else:
        print("    ✅ 无孤立记录")

    # 检查 similar_questions 表中的孤立记录
    print()
    print("[2] 检查 similar_questions 表...")
    cursor.execute('''
        SELECT COUNT(*) FROM similar_questions sq
        WHERE sq.exam_id NOT IN (SELECT exam_id FROM exams)
    ''')
    orphan_similar = cursor.fetchone()[0]
    
    if orphan_similar > 0:
        print(f"    ❌ 发现 {orphan_similar} 条孤立记录（exam_id 不存在）")
        cursor.execute('''
            SELECT similar_id, exam_id, title, created_at
            FROM similar_questions sq
            WHERE sq.exam_id NOT IN (SELECT exam_id FROM exams)
            LIMIT 5
        ''')
        for row in cursor.fetchall():
            print(f"      - {row[0][:20]}... (exam_id: {row[1][:20]}...)")
    else:
        print("    ✅ 无孤立记录")

    # 检查 teacher_collections 表中的孤立记录
    print()
    print("[3] 检查 teacher_collections 表...")
    cursor.execute('''
        SELECT COUNT(*) FROM teacher_collections tc
        WHERE tc.question_id NOT IN (SELECT question_id FROM questions)
    ''')
    orphan_collections = cursor.fetchone()[0]
    
    if orphan_collections > 0:
        print(f"    ❌ 发现 {orphan_collections} 条孤立记录（question_id 不存在）")
    else:
        print("    ✅ 无孤立记录")

    # 统计当前数据
    print()
    print("=" * 60)
    print("当前数据统计")
    print("=" * 60)
    
    tables = ['users', 'exams', 'questions', 'similar_questions', 
               'teacher_collections', 'collection_tags', 'teacher_folders']
    
    for table in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} 条")
        except Exception as e:
            print(f"  {table}: 检查失败 ({e})")

    conn.close()
    print()

    # 返回是否有脏数据
    total_orphan = orphan_questions + orphan_similar + orphan_collections
    return total_orphan


def clean_orphan_data():
    """清理孤立数据"""
    print("=" * 60)
    print("开始清理孤立数据")
    print("=" * 60)
    print()

    conn = get_db_connection()
    cursor = conn.cursor()

    total_deleted = 0

    # 清理 questions 表中的孤立记录
    print("[1] 清理 questions 表孤立记录...")
    cursor.execute('''
        DELETE FROM questions
        WHERE exam_id NOT IN (SELECT exam_id FROM exams)
    ''')
    deleted = cursor.rowcount
    total_deleted += deleted
    if deleted > 0:
        print(f"    ✅ 删除了 {deleted} 条记录")
    else:
        print("    ✅ 无需清理")

    # 清理 similar_questions 表中的孤立记录
    print()
    print("[2] 清理 similar_questions 表孤立记录...")
    cursor.execute('''
        DELETE FROM similar_questions
        WHERE exam_id NOT IN (SELECT exam_id FROM exams)
    ''')
    deleted = cursor.rowcount
    total_deleted += deleted
    if deleted > 0:
        print(f"    ✅ 删除了 {deleted} 条记录")
    else:
        print("    ✅ 无需清理")

    # 清理 teacher_collections 表中的孤立记录
    print()
    print("[3] 清理 teacher_collections 表孤立记录...")
    cursor.execute('''
        DELETE FROM teacher_collections
        WHERE question_id NOT IN (SELECT question_id FROM questions)
    ''')
    deleted = cursor.rowcount
    total_deleted += deleted
    if deleted > 0:
        print(f"    ✅ 删除了 {deleted} 条记录")
    else:
        print("    ✅ 无需清理")

    conn.commit()
    conn.close()

    print()
    print("=" * 60)
    print(f"✅ 清理完成！共删除 {total_deleted} 条孤立记录")
    print("=" * 60)
    print()

    return total_deleted


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--clean':
        # 执行清理
        orphan_count = check_integrity()
        if orphan_count > 0:
            print()
            response = input("是否清理这些孤立数据？(y/N): ")
            if response.lower() == 'y':
                clean_orphan_data()
            else:
                print("已取消清理")
        else:
            print("✅ 数据库完整性良好，无需清理")
    else:
        # 仅检查
        orphan_count = check_integrity()
        if orphan_count > 0:
            print()
            print("💡 提示：使用 --clean 参数可以自动清理孤立数据")
            print("    例如: python db_integrity_check.py --clean")
        else:
            print("✅ 数据库完整性良好")


if __name__ == "__main__":
    main()
