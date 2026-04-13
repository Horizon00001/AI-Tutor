import uuid
from datetime import datetime
from typing import Dict, Optional, List, Any
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskType(str, Enum):
    MINERU = "mineru"
    DEEPSEEK = "deepseek"
    PPT = "ppt"
    SIMILAR_QUESTION = "similar_question"

class Task:
    def __init__(self, task_type: TaskType, source_id: str = None):
        self.task_id = str(uuid.uuid4())
        self.task_type = task_type
        self.source_id = source_id
        self.status = TaskStatus.PENDING
        self.progress = 0
        self.current_step = "等待中"
        self.result_file = None
        self.error = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.completed_at = None
        self.data = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "source_id": self.source_id,
            "status": self.status.value,
            "progress": self.progress,
            "current_step": self.current_step,
            "result_file": self.result_file,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "data": self.data
        }

    def update_status(self, status: TaskStatus, progress: int = None, step: str = None):
        self.status = status
        self.updated_at = datetime.now()
        if progress is not None:
            self.progress = progress
        if step is not None:
            self.current_step = step
        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            self.completed_at = datetime.now()

    def set_error(self, error: str):
        self.error = error
        self.update_status(TaskStatus.FAILED)

    def set_result(self, result_file: str, data: dict = None):
        self.result_file = result_file
        if data:
            self.data = data
        self.update_status(TaskStatus.COMPLETED, progress=100)

class TaskManager:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    def create_task(self, task_type: TaskType, source_id: str = None) -> Task:
        task = Task(task_type, source_id)
        self._tasks[task.task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_tasks(self, task_type: TaskType = None, status: TaskStatus = None) -> List[Task]:
        tasks = list(self._tasks.values())
        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    def delete_task(self, task_id: str) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

task_manager = TaskManager()
