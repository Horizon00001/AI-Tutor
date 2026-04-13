import uuid
from typing import Optional, List, Dict
from services.database import (
    create_teacher_folder, get_teacher_folders, get_folder_by_id,
    update_teacher_folder, delete_teacher_folder, move_folder_to_root
)


class CollectionFolderService:
    """收藏文件夹服务"""

    def create_folder(self, teacher_id: str, name: str, parent_id: str = None, color: str = None) -> Dict:
        """创建文件夹"""
        folder_id = str(uuid.uuid4())
        success = create_teacher_folder(folder_id, teacher_id, name, parent_id, color)
        
        if not success:
            return {"success": False, "error": "创建文件夹失败"}
        
        return {
            "success": True,
            "folder_id": folder_id,
            "name": name,
            "parent_id": parent_id,
            "color": color or '#1890ff'
        }

    def get_folders(self, teacher_id: str) -> List[Dict]:
        """获取文件夹树形结构"""
        folders = get_teacher_folders(teacher_id)
        
        # 构建树形结构
        folder_map = {}
        root_folders = []
        
        for folder in folders:
            folder_id = folder['folder_id']
            folder['children'] = []
            folder_map[folder_id] = folder
        
        for folder in folders:
            parent_id = folder.get('parent_id')
            if parent_id and parent_id in folder_map:
                folder_map[parent_id]['children'].append(folder)
            else:
                root_folders.append(folder)
        
        return root_folders

    def get_folder_detail(self, folder_id: str, teacher_id: str) -> Optional[Dict]:
        """获取文件夹详情"""
        folder = get_folder_by_id(folder_id, teacher_id)
        if not folder:
            return None
        return dict(folder)

    def update_folder(self, folder_id: str, teacher_id: str, name: str = None, 
                      color: str = None, parent_id: str = None) -> Dict:
        """更新文件夹"""
        # 检查文件夹是否存在
        folder = get_folder_by_id(folder_id, teacher_id)
        if not folder:
            return {"success": False, "error": "文件夹不存在"}
        
        # 检查循环引用（不能将文件夹移动到自己的子文件夹中）
        if parent_id:
            if parent_id == folder_id:
                return {"success": False, "error": "不能将文件夹移动到自己"}
            
            # 检查目标文件夹是否是当前文件夹的子文件夹
            if self._is_descendant(folder_id, parent_id, teacher_id):
                return {"success": False, "error": "不能将文件夹移动到自己的子文件夹中"}
        
        success = update_teacher_folder(folder_id, teacher_id, name, color, parent_id)
        
        if not success:
            return {"success": False, "error": "更新文件夹失败"}
        
        return {"success": True}

    def delete_folder(self, folder_id: str, teacher_id: str, move_to_root: bool = True) -> Dict:
        """删除文件夹"""
        # 检查文件夹是否存在
        folder = get_folder_by_id(folder_id, teacher_id)
        if not folder:
            return {"success": False, "error": "文件夹不存在"}
        
        # 如果需要，将子文件夹移动到根目录
        if move_to_root:
            move_folder_to_root(folder_id, teacher_id)
        
        success = delete_teacher_folder(folder_id, teacher_id)
        
        if not success:
            return {"success": False, "error": "删除文件夹失败"}
        
        return {"success": True}

    def move_folder(self, folder_id: str, teacher_id: str, parent_id: str) -> Dict:
        """移动文件夹"""
        return self.update_folder(folder_id, teacher_id, parent_id=parent_id)

    def _is_descendant(self, ancestor_id: str, target_id: str, teacher_id: str) -> bool:
        """检查target_id是否是ancestor_id的后代"""
        folders = get_teacher_folders(teacher_id)
        folder_map = {f['folder_id']: f for f in folders}
        
        current_id = target_id
        while current_id:
            folder = folder_map.get(current_id)
            if not folder:
                break
            if folder.get('parent_id') == ancestor_id:
                return True
            current_id = folder.get('parent_id')
        
        return False


folder_service = CollectionFolderService()
