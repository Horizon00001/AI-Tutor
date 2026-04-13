from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime

from api.models.schemas import (
    CreateFolderRequest, FolderResponse,
    CollectQuestionRequest, CollectionResponse, CollectionListResponse,
    UpdateCollectionRequest, CreateTagRequest, TagResponse,
    CollectionStatsResponse, BatchMoveRequest, BatchDeleteRequest,
    BatchOperationResponse
)
from services.collection_service import collection_service
from services.collection_folder_service import folder_service
from services.collection_tag_service import tag_service

router = APIRouter(prefix="/collections", tags=["题目收藏"])


# ==================== 统计（放在最前面避免路由冲突） ====================

@router.get("/stats/summary", response_model=CollectionStatsResponse)
async def get_stats(teacher_id: str):
    """获取收藏统计信息"""
    stats = collection_service.get_stats(teacher_id)
    return CollectionStatsResponse(**stats)


# ==================== 文件夹管理 ====================

@router.post("/folders", response_model=dict)
async def create_folder(request: CreateFolderRequest):
    """创建收藏文件夹"""
    result = folder_service.create_folder(
        teacher_id=request.teacher_id,
        name=request.name,
        parent_id=request.parent_id,
        color=request.color
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/folders", response_model=List[FolderResponse])
async def get_folders(teacher_id: str):
    """获取文件夹树形结构"""
    folders = folder_service.get_folders(teacher_id)
    return folders


@router.get("/folders/{folder_id}", response_model=dict)
async def get_folder_detail(folder_id: str, teacher_id: str):
    """获取文件夹详情"""
    folder = folder_service.get_folder_detail(folder_id, teacher_id)
    if not folder:
        raise HTTPException(status_code=404, detail="文件夹不存在")
    return {"success": True, "folder": folder}


@router.put("/folders/{folder_id}", response_model=dict)
async def update_folder(folder_id: str, request: dict):
    """更新文件夹"""
    teacher_id = request.get("teacher_id")
    if not teacher_id:
        raise HTTPException(status_code=400, detail="缺少teacher_id")
    
    result = folder_service.update_folder(
        folder_id=folder_id,
        teacher_id=teacher_id,
        name=request.get("name"),
        color=request.get("color"),
        parent_id=request.get("parent_id")
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.delete("/folders/{folder_id}", response_model=dict)
async def delete_folder(folder_id: str, teacher_id: str, move_to_root: bool = True):
    """删除文件夹"""
    result = folder_service.delete_folder(folder_id, teacher_id, move_to_root)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.put("/folders/{folder_id}/move", response_model=dict)
async def move_folder(folder_id: str, request: dict):
    """移动文件夹"""
    teacher_id = request.get("teacher_id")
    parent_id = request.get("parent_id")
    
    if not teacher_id:
        raise HTTPException(status_code=400, detail="缺少teacher_id")
    
    result = folder_service.move_folder(folder_id, teacher_id, parent_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


# ==================== 标签管理（放在收藏详情路由之前） ====================

@router.post("/tags", response_model=dict)
async def create_tag(request: CreateTagRequest):
    """创建标签"""
    result = tag_service.create_tag(
        teacher_id=request.teacher_id,
        tag_name=request.tag_name,
        color=request.color
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/tags", response_model=List[TagResponse])
async def get_tags(teacher_id: str):
    """获取标签列表"""
    tags = tag_service.get_tags(teacher_id)
    return tags


@router.get("/tags/{tag_id}", response_model=dict)
async def get_tag_detail(tag_id: str, teacher_id: str):
    """获取标签详情"""
    tag = tag_service.get_tag_detail(tag_id, teacher_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return {"success": True, "tag": tag}


@router.put("/tags/{tag_id}", response_model=dict)
async def update_tag(tag_id: str, request: dict):
    """更新标签"""
    teacher_id = request.get("teacher_id")
    if not teacher_id:
        raise HTTPException(status_code=400, detail="缺少teacher_id")
    
    result = tag_service.update_tag(
        tag_id=tag_id,
        teacher_id=teacher_id,
        tag_name=request.get("tag_name"),
        color=request.get("color")
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.delete("/tags/{tag_id}", response_model=dict)
async def delete_tag(tag_id: str, teacher_id: str):
    """删除标签"""
    result = tag_service.delete_tag(tag_id, teacher_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


# ==================== 批量操作（放在收藏详情路由之前） ====================

@router.post("/batch-move", response_model=BatchOperationResponse)
async def batch_move(request: BatchMoveRequest):
    """批量移动收藏到文件夹"""
    result = collection_service.batch_move(
        collection_ids=request.collection_ids,
        folder_id=request.folder_id,
        teacher_id=request.teacher_id
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return BatchOperationResponse(
        success=True,
        affected_count=result.get("affected_count", 0)
    )


@router.post("/batch-delete", response_model=BatchOperationResponse)
async def batch_delete(request: BatchDeleteRequest):
    """批量删除收藏"""
    result = collection_service.batch_delete(
        collection_ids=request.collection_ids,
        teacher_id=request.teacher_id
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return BatchOperationResponse(
        success=True,
        affected_count=result.get("affected_count", 0)
    )


# ==================== 检查题目是否已收藏（放在收藏详情路由之前） ====================

@router.get("/check/{question_id}", response_model=dict)
async def check_collected(question_id: str, teacher_id: str):
    """检查题目是否已收藏"""
    from services.database import is_question_collected
    is_collected = is_question_collected(teacher_id, question_id)
    return {
        "question_id": question_id,
        "is_collected": is_collected
    }


# ==================== 题目收藏（基础CRUD放在最后） ====================

@router.post("", response_model=dict)
async def collect_question(request: CollectQuestionRequest):
    """收藏题目"""
    result = collection_service.collect_question(
        teacher_id=request.teacher_id,
        question_id=request.question_id,
        folder_id=request.folder_id,
        tags=request.tags,
        difficulty_note=request.difficulty_note,
        teach_note=request.teach_note,
        common_errors=request.common_errors,
        teach_points=request.teach_points
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("", response_model=dict)
async def get_collections(
    teacher_id: str,
    folder_id: Optional[str] = None,
    tag: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """获取收藏列表"""
    result = collection_service.get_collections(
        teacher_id=teacher_id,
        folder_id=folder_id,
        tag=tag,
        keyword=keyword,
        page=page,
        limit=limit
    )
    return result


@router.get("/{collection_id}", response_model=dict)
async def get_collection_detail(collection_id: str, teacher_id: str):
    """获取收藏详情"""
    collection = collection_service.get_collection_detail(collection_id, teacher_id)
    if not collection:
        raise HTTPException(status_code=404, detail="收藏不存在")
    return {"success": True, "collection": collection}


@router.put("/{collection_id}", response_model=dict)
async def update_collection(collection_id: str, request: UpdateCollectionRequest):
    """更新收藏信息"""
    # 从请求头或其他方式获取teacher_id，这里简化处理
    # 实际项目中应该从认证信息中获取
    raise HTTPException(status_code=400, detail="请使用包含teacher_id的请求体")


@router.put("/{collection_id}/update", response_model=dict)
async def update_collection_with_teacher(collection_id: str, request: dict):
    """更新收藏信息（带teacher_id）"""
    teacher_id = request.get("teacher_id")
    if not teacher_id:
        raise HTTPException(status_code=400, detail="缺少teacher_id")
    
    result = collection_service.update_collection_info(
        collection_id=collection_id,
        teacher_id=teacher_id,
        folder_id=request.get("folder_id"),
        tags=request.get("tags"),
        difficulty_note=request.get("difficulty_note"),
        teach_note=request.get("teach_note"),
        common_errors=request.get("common_errors"),
        teach_points=request.get("teach_points")
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.delete("/{collection_id}", response_model=dict)
async def delete_collection(collection_id: str, teacher_id: str):
    """取消收藏"""
    result = collection_service.delete_collection_item(collection_id, teacher_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/{collection_id}/record-usage", response_model=dict)
async def record_usage(collection_id: str, teacher_id: str):
    """记录收藏使用次数"""
    result = collection_service.record_usage(collection_id, teacher_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result
