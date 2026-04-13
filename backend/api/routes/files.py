from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import List
from datetime import datetime
from pathlib import Path

from api.models.schemas import FileUploadResponse, FileListResponse
from utils.file_handler import file_handler
from utils.storage import storage

router = APIRouter(prefix="/files", tags=["文件管理"])

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()

    is_valid, error_msg = file_handler.validate_file(file.filename, content)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    file_id = file_handler.generate_file_id()
    file_path = storage.save_uploaded_file(file_id, file.filename, content)

    return FileUploadResponse(
        file_id=file_id,
        filename=file.filename,
        file_type=file_handler.get_file_type(file.filename),
        file_size=len(content),
        upload_time=datetime.now(),
        status="uploaded"
    )

@router.get("", response_model=FileListResponse)
async def list_files(page: int = 1, limit: int = 20, file_type: str = "all"):
    all_files = storage.list_uploaded_files()

    if file_type != "all":
        all_files = [f for f in all_files if file_handler.get_file_type(f["filename"]) == file_type]

    total = len(all_files)
    start = (page - 1) * limit
    end = start + limit
    files = all_files[start:end]

    return FileListResponse(
        total=total,
        page=page,
        limit=limit,
        files=files
    )

@router.get("/{file_id}")
async def get_file_info(file_id: str):
    file_path = storage.get_uploaded_file(file_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="文件不存在")

    return {
        "file_id": file_id,
        "filename": "_".join(file_path.name.split("_")[1:]),
        "file_type": file_handler.get_file_type(file_path.name),
        "file_size": file_path.stat().st_size,
        "upload_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
    }

@router.get("/{file_id}/download")
async def download_file(file_id: str):
    file_path = storage.get_uploaded_file(file_id)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    filename = "_".join(file_path.name.split("_")[1:])
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

@router.delete("/{file_id}")
async def delete_file(file_id: str):
    if storage.delete_uploaded_file(file_id):
        return {"message": "文件已删除", "file_id": file_id}
    raise HTTPException(status_code=404, detail="文件不存在")
