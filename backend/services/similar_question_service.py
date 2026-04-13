import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from openai import OpenAI
from services.task_manager import task_manager, TaskType, TaskStatus
from services.exam_service import save_similar_questions
from utils.config import API_KEY, API_URL
from utils.storage import storage

class SimilarQuestionService:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=API_URL)

    async def generate_similar(
        self,
        source_question: Dict[str, Any],
        source_question_id: str,
        exam_id: str,
        user_id: str,
        count: int,
        difficulty_adjustment: str,
        preserve_knowledge_points: bool,
        task_id: str
    ) -> Optional[List[Dict]]:
        task = task_manager.get_task(task_id)
        if not task:
            return None

        try:
            task.update_status(TaskStatus.PROCESSING, progress=10, step="准备生成相似题...")

            difficulty_prompt = ""
            if difficulty_adjustment == "easier":
                difficulty_prompt = "请生成难度较低的相似题，侧重基础知识点"
            elif difficulty_adjustment == "harder":
                difficulty_prompt = "请生成难度较高的相似题，增加综合性或创新性"
            else:
                difficulty_prompt = "请生成难度相同的相似题"

            prompt = f"""
请根据以下原题生成{count}道相似题。

原题信息:
- 标题: {source_question.get('title', '')}
- 内容: {source_question.get('content', '')}
- 答案: {source_question.get('answer', '')}
- 解析: {source_question.get('analysis', '')}

{difficulty_prompt}

要求:
1. 保持相似的知识点, 但不完全相同,有所变化
2. 改变数据、情境或表述方式
3. 每道题必须包含: title, content, answer, analysis字段
4. 以JSON数组格式返回结果

返回格式:
{{"similar_questions": [{{"title": "...", "content": "...", "answer": "...", "analysis": "..."}}]}}
"""

            task.update_status(TaskStatus.PROCESSING, progress=30, step="调用DeepSeek API...")

            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            task.update_status(TaskStatus.PROCESSING, progress=70, step="解析生成结果...")

            result = json.loads(response.choices[0].message.content)
            similar_questions = result.get("similar_questions", [])

            for q in similar_questions:
                q["difficulty"] = difficulty_adjustment
                q["knowledge_points"] = []

            task.update_status(TaskStatus.PROCESSING, progress=90, step="保存相似题到文件...")

            result_file = storage.save_similar_questions(task_id, source_question, similar_questions)

            # 保存到数据库
            save_similar_questions(
                source_question_id=source_question_id,
                exam_id=exam_id,
                user_id=user_id,
                similar_questions=similar_questions
            )

            task.update_status(TaskStatus.COMPLETED, progress=100, step="完成")
            task.set_result(str(result_file), {
                "similar_questions": similar_questions,
                "generated_count": len(similar_questions),
                "source_question": source_question
            })

            return similar_questions

        except Exception as e:
            task.set_error(str(e))
            return None

similar_question_service = SimilarQuestionService()
