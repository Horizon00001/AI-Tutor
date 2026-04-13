import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from openai import OpenAI
from pydantic import BaseModel, Field
from services.task_manager import task_manager, TaskType, TaskStatus
from utils.config import API_KEY, API_URL, PROCESSED_JSON_DIR, PROMPT_PATH
from utils.storage import storage

class Question(BaseModel):
    title: str = Field(..., description="题目编号或所属大题标题")
    source: str = Field(..., description="题目来源，如试卷名称、书籍名称等，同一试卷题目来源相同")
    content: str = Field(..., description="修复后的完整题干。包含已知条件、子题目列表或选项。数学/专业符号必须使用 LaTeX ($ 或 $$)。")
    answer: str = Field(..., description="该题的参考答案或计算结果。")
    analysis: str = Field(..., description="该题的核心知识点解析与逻辑推导过程。")

class DeepSeekService:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=API_URL)
        self.prompt_path = PROMPT_PATH

    async def fix_json(self, json_file_path: Path, task_id: str) -> Optional[Path]:
        task = task_manager.get_task(task_id)
        if not task:
            return None

        try:
            task.update_status(TaskStatus.PROCESSING, progress=10, step="读取JSON文件...")

            with open(json_file_path, 'r', encoding='utf-8') as f:
                ocr_data = f.read()

            task.update_status(TaskStatus.PROCESSING, progress=20, step="加载系统提示词...")

            with open(self.prompt_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()

            task.update_status(TaskStatus.PROCESSING, progress=30, step="调用DeepSeek API...")

            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"以下是需要处理的 OCR JSON 数据：\n\n{ocr_data}"}
                ],
                response_format={"type": "json_object"},
                stream=False
            )

            task.update_status(TaskStatus.PROCESSING, progress=70, step="解析API响应...")

            content = response.choices[0].message.content
            data = json.loads(content)

            if isinstance(data, dict) and "questions" in data:
                items = data["questions"]
            elif isinstance(data, list):
                items = data
            else:
                items = [data] if isinstance(data, dict) else []

            questions = [Question(**item) for item in items]

            task.update_status(TaskStatus.PROCESSING, progress=90, step="保存结果...")

            file_stem = json_file_path.stem
            output_file = PROCESSED_JSON_DIR / f"{file_stem}_cleaned.json"

            result_json = [q.model_dump() for q in questions]
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result_json, f, ensure_ascii=False, indent=2)

            task.update_status(TaskStatus.COMPLETED, progress=100, step="完成")
            task.set_result(str(output_file), {"questions": result_json, "count": len(questions)})

            return output_file

        except Exception as e:
            task.set_error(str(e))
            return None

    def get_questions_from_task(self, task_id: str) -> Optional[List[Dict]]:
        task = task_manager.get_task(task_id)
        if not task or task.status != TaskStatus.COMPLETED:
            return None

        if task.data and "questions" in task.data:
            return task.data["questions"]

        if task.result_file:
            return storage.read_json(Path(task.result_file))

        return None

deepseek_service = DeepSeekService()
