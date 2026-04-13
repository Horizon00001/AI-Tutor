import aiofiles
from pathlib import Path
from typing import Optional
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
