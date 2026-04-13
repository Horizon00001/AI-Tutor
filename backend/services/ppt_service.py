import json
from pathlib import Path
from typing import Optional

from .task_manager import task_manager, TaskType, TaskStatus
from .ppt_generator import ppt_generator
from utils.config import PPT_DIR


class PPTService:
    def __init__(self):
        self.ppt_dir = PPT_DIR

    async def generate(self, json_file_path: Path, use_animation: bool, title: str, task_id: str) -> Optional[Path]:
        task = task_manager.get_task(task_id)
        if not task:
            return None

        try:
            task.update_status(TaskStatus.PROCESSING, progress=10, step="读取JSON文件...")

            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                questions = data
            else:
                questions = data.get('questions', data)

            task.update_status(TaskStatus.PROCESSING, progress=30, step="生成PPT...")

            output_path = self.ppt_dir / f"{json_file_path.stem}_fixed.pptx"

            ppt_generator.generate(
                questions=questions,
                output_path=output_path,
                title=title,
                use_animation=use_animation
            )

            if not output_path.exists():
                raise RuntimeError("PPT生成失败")

            task.update_status(TaskStatus.COMPLETED, progress=100, step="完成")
            task.set_result(str(output_path), {
                "slide_count": len(questions) + 1,
                "questions_count": len(questions)
            })

            return output_path

        except Exception as e:
            task.set_error(str(e))
            return None


ppt_service = PPTService()
