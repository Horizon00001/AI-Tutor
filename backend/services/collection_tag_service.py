import uuid
from typing import Optional, List, Dict
from services.database import (
    create_collection_tag, get_collection_tags, get_tag_by_id,
    update_collection_tag, delete_collection_tag
)


class CollectionTagService:
    """收藏标签服务"""

    def create_tag(self, teacher_id: str, tag_name: str, color: str = None) -> Dict:
        """创建标签"""
        tag_id = str(uuid.uuid4())
        success = create_collection_tag(tag_id, teacher_id, tag_name, color)
        
        if not success:
            return {"success": False, "error": "标签已存在或创建失败"}
        
        return {
            "success": True,
            "tag_id": tag_id,
            "tag_name": tag_name,
            "color": color or '#52c41a'
        }

    def get_tags(self, teacher_id: str) -> List[Dict]:
        """获取标签列表"""
        return get_collection_tags(teacher_id)

    def get_tag_detail(self, tag_id: str, teacher_id: str) -> Optional[Dict]:
        """获取标签详情"""
        tag = get_tag_by_id(tag_id, teacher_id)
        if not tag:
            return None
        return dict(tag)

    def update_tag(self, tag_id: str, teacher_id: str, tag_name: str = None, 
                   color: str = None) -> Dict:
        """更新标签"""
        # 检查标签是否存在
        tag = get_tag_by_id(tag_id, teacher_id)
        if not tag:
            return {"success": False, "error": "标签不存在"}
        
        success = update_collection_tag(tag_id, teacher_id, tag_name, color)
        
        if not success:
            return {"success": False, "error": "更新失败，标签名可能已存在"}
        
        return {"success": True}

    def delete_tag(self, tag_id: str, teacher_id: str) -> Dict:
        """删除标签"""
        tag = get_tag_by_id(tag_id, teacher_id)
        if not tag:
            return {"success": False, "error": "标签不存在"}
        
        success = delete_collection_tag(tag_id, teacher_id)
        
        if not success:
            return {"success": False, "error": "删除失败"}
        
        return {"success": True}


tag_service = CollectionTagService()
