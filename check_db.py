#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('data/data.db')
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('=== 数据库中的所有表 ===')
for row in cursor.fetchall():
    print(f'  - {row[0]}')

print()

# 查看exams表结构
cursor.execute('PRAGMA table_info(exams)')
print('=== exams 表结构 ===')
for row in cursor.fetchall():
    print(f'  {row[1]} ({row[2]})')

print()

# 查看exams表数据
cursor.execute('SELECT exam_id, user_id, source, created_at FROM exams ORDER BY created_at DESC LIMIT 5')
print('=== exams 表数据 (最近5条) ===')
for row in cursor.fetchall():
    print(f'  exam_id: {row[0][:20]}...')
    print(f'    user_id: {row[1][:20]}...')
    print(f'    source: {row[2]}')
    print(f'    created_at: {row[3]}')
    print()

# 查看questions表结构
cursor.execute('PRAGMA table_info(questions)')
print('=== questions 表结构 ===')
for row in cursor.fetchall():
    print(f'  {row[1]} ({row[2]})')

print()

# 查看questions表数据
cursor.execute('SELECT question_id, exam_id, title, content, answer FROM questions ORDER BY created_at DESC LIMIT 3')
print('=== questions 表数据 (最近3条) ===')
for row in cursor.fetchall():
    print(f'  question_id: {row[0][:20]}...')
    print(f'    exam_id: {row[1][:20]}...')
    print(f'    title: {row[2]}')
    print(f'    content: {row[3][:80]}...')
    print(f'    answer: {row[4]}')
    print()

# 查看similar_questions表结构
cursor.execute('PRAGMA table_info(similar_questions)')
print('=== similar_questions 表结构 ===')
for row in cursor.fetchall():
    print(f'  {row[1]} ({row[2]})')

print()

# 查看similar_questions表数据
cursor.execute('SELECT similar_id, source_question_id, exam_id, title, difficulty FROM similar_questions ORDER BY created_at DESC LIMIT 3')
print('=== similar_questions 表数据 (最近3条) ===')
for row in cursor.fetchall():
    print(f'  similar_id: {row[0][:20]}...')
    print(f'    source_question_id: {row[1][:20]}...')
    print(f'    exam_id: {row[2][:20]}...')
    print(f'    title: {row[3]}')
    print(f'    difficulty: {row[4]}')
    print()

# 统计
cursor.execute('SELECT COUNT(*) FROM exams')
exam_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM questions')
question_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM similar_questions')
similar_count = cursor.fetchone()[0]

print('=== 数据统计 ===')
print(f'  试卷总数: {exam_count}')
print(f'  题目总数: {question_count}')
print(f'  相似题总数: {similar_count}')

conn.close()
