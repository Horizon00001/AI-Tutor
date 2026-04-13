import aiofiles
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile
from utils.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, UPLOAD_DIR


class FileHandler:
    """文件处理工具"""

    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        """检查文件扩展名是否允许"""
        return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def get_file_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    @staticmethod
    def validate_file(filename: str, content: bytes) -> Tuple[bool, str]:
        """验证文件是否合法"""
        if not filename:
            return False, "文件名为空"
        if not FileHandler.is_allowed_file(filename):
            return False, f"不支持的文件类型，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"
        if len(content) > MAX_FILE_SIZE:
            return False, f"文件大小超过限制 ({MAX_FILE_SIZE // 1024 // 1024}MB)"
        return True, ""

    @staticmethod
    def generate_file_id() -> str:
        """生成唯一文件ID"""
        return str(uuid.uuid4())

    @staticmethod
    async def save_upload_file(file: UploadFile, dest_path: Path) -> bool:
        """保存上传文件"""
        try:
            async with aiofiles.open(dest_path, 'wb') as out_file:
                content = await file.read()
                if len(content) > MAX_FILE_SIZE:
                    return False
                await out_file.write(content)
            return True
        except Exception:
            return False

    @staticmethod
    def delete_file(file_path: Path) -> bool:
        """删除文件"""
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False


file_handler = FileHandler()
