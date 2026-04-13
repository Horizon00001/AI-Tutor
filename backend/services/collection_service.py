import json
import uuid
from typing import Optional, List, Dict
from services.database import (
    create_collection, get_collection_by_id, get_collections_by_teacher,
    update_collection, delete_collection, record_collection_usage,
    move_collections_to_folder, batch_delete_collections, is_question_collected,
    get_question_by_id, get_collection_stats
)


class CollectionService:
    """题目收藏服务"""

    def collect_question(self, teacher_id: str, question_id: str, folder_id: str = None,
                        tags: List[str] = None, difficulty_note: str = None,
                        teach_note: str = None, common_errors: str = None,
                        teach_points: str = None) -> Dict:
        """收藏题目"""
        # 检查是否已收藏
        if is_question_collected(teacher_id, question_id):
            return {"success": False, "error": "该题目已收藏"}
        
        # 获取题目信息
        question = get_question_by_id(question_id)
        if not question:
            return {"success": False, "error": "题目不存在"}
        
        collection_id = str(uuid.uuid4())
        tags_json = json.dumps(tags, ensure_ascii=False) if tags else None
        
        success = create_collection(
            collection_id=collection_id,
            teacher_id=teacher_id,
            question_id=question_id,
            folder_id=folder_id,
            title=question.get('title'),
            content=question.get('content'),
            answer=question.get('answer'),
            analysis=question.get('analysis'),
            tags=tags_json,
            difficulty_note=difficulty_note,
            teach_note=teach_note,
            common_errors=common_errors,
            teach_points=teach_points
        )
        
        if not success:
            return {"success": False, "error": "收藏失败"}
        
        return {
            "success": True,
            "collection_id": collection_id,
            "question_id": question_id,
            "folder_id": folder_id
        }

    def get_collections(self, teacher_id: str, folder_id: str = None, tag: str = None,
                       keyword: str = None, page: int = 1, limit: int = 20) -> Dict:
        """获取收藏列表"""
        total, collections = get_collections_by_teacher(
            teacher_id=teacher_id,
            folder_id=folder_id,
            tag=tag,
            keyword=keyword,
            page=page,
            limit=limit
        )
        
        # 处理tags字段
        for collection in collections:
            if collection.get('tags'):
                try:
                    collection['tags'] = json.loads(collection['tags'])
                except json.JSONDecodeError:
                    collection['tags'] = []
            else:
                collection['tags'] = []
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "collections": collections
        }

    def get_collection_detail(self, collection_id: str, teacher_id: str) -> Optional[Dict]:
        """获取收藏详情"""
        collection = get_collection_by_id(collection_id, teacher_id)
        if not collection:
            return None
        
        # 处理tags字段
        if collection.get('tags'):
            try:
                collection['tags'] = json.loads(collection['tags'])
            except json.JSONDecodeError:
                collection['tags'] = []
        else:
            collection['tags'] = []
        
        return collection

    def update_collection_info(self, collection_id: str, teacher_id: str, **kwargs) -> Dict:
        """更新收藏信息"""
        # 检查收藏是否存在
        collection = get_collection_by_id(collection_id, teacher_id)
        if not collection:
            return {"success": False, "error": "收藏不存在"}
        
        # 处理tags字段
        if 'tags' in kwargs and kwargs['tags'] is not None:
            kwargs['tags'] = json.dumps(kwargs['tags'], ensure_ascii=False)
        
        success = update_collection(collection_id, teacher_id, **kwargs)
        
        if not success:
            return {"success": False, "error": "更新失败"}
        
        return {"success": True}

    def delete_collection_item(self, collection_id: str, teacher_id: str) -> Dict:
        """取消收藏"""
        collection = get_collection_by_id(collection_id, teacher_id)
        if not collection:
            return {"success": False, "error": "收藏不存在"}
        
        success = delete_collection(collection_id, teacher_id)
        
        if not success:
            return {"success": False, "error": "删除失败"}
        
        return {"success": True}

    def batch_move(self, collection_ids: List[str], folder_id: str, teacher_id: str) -> Dict:
        """批量移动收藏到文件夹"""
        if not collection_ids:
            return {"success": False, "error": "未选择任何收藏"}
        
        affected = move_collections_to_folder(collection_ids, folder_id, teacher_id)
        
        return {
            "success": True,
            "affected_count": affected
        }

    def batch_delete(self, collection_ids: List[str], teacher_id: str) -> Dict:
        """批量删除收藏"""
        if not collection_ids:
            return {"success": False, "error": "未选择任何收藏"}
        
        affected = batch_delete_collections(collection_ids, teacher_id)
        
        return {
            "success": True,
            "affected_count": affected
        }

    def record_usage(self, collection_id: str, teacher_id: str) -> Dict:
        """记录收藏使用次数"""
        success = record_collection_usage(collection_id, teacher_id)
        
        if not success:
            return {"success": False, "error": "记录失败"}
        
        return {"success": True}

    def get_stats(self, teacher_id: str) -> Dict:
        """获取收藏统计信息"""
        return get_collection_stats(teacher_id)


collection_service = CollectionService()
