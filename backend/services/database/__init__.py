"""
数据库模块 - 拆分后的数据库操作

子模块:
- connection: 数据库连接配置
- init: 表初始化
- user: 用户相关操作
- exam: 试卷相关操作
- question: 题目相关操作
- similar: 相似题相关操作
- collection: 收藏相关操作（文件夹、收藏、标签）
- stats: 统计相关操作
"""

# 连接配置
from services.database.connection import get_db_connection, DATABASE_PATH, DATA_DIR

# 初始化
from services.database.init import init_db

# 用户
from services.database.user import (
    create_user,
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
)

# 试卷
from services.database.exam import (
    create_exam,
    get_exam_by_id,
    list_user_exams,
    delete_exam,
)

# 题目
from services.database.question import (
    create_question,
    get_question_by_id,
    get_questions_by_exam,
    update_question,
    get_questions_count_by_exam,
)

# 相似题
from services.database.similar import (
    create_similar_question,
    get_similar_questions_by_source,
    get_similar_questions_by_exam,
)

# 收藏
from services.database.collection import (
    init_collection_tables,
    create_teacher_folder,
    get_teacher_folders,
    get_folder_by_id,
    update_teacher_folder,
    delete_teacher_folder,
    move_folder_to_root,
    create_collection,
    get_collection_by_id,
    get_collections_by_teacher,
    update_collection,
    delete_collection,
    record_collection_usage,
    move_collections_to_folder,
    batch_delete_collections,
    is_question_collected,
    create_collection_tag,
    get_collection_tags,
    get_tag_by_id,
    update_collection_tag,
    delete_collection_tag,
)

# 统计
from services.database.stats import get_collection_stats

__all__ = [
    # 连接
    "get_db_connection",
    "DATABASE_PATH",
    "DATA_DIR",
    # 初始化
    "init_db",
    # 用户
    "create_user",
    "get_user_by_username",
    "get_user_by_email",
    "get_user_by_id",
    # 试卷
    "create_exam",
    "get_exam_by_id",
    "list_user_exams",
    "delete_exam",
    # 题目
    "create_question",
    "get_question_by_id",
    "get_questions_by_exam",
    "update_question",
    "get_questions_count_by_exam",
    # 相似题
    "create_similar_question",
    "get_similar_questions_by_source",
    "get_similar_questions_by_exam",
    # 收藏
    "init_collection_tables",
    "create_teacher_folder",
    "get_teacher_folders",
    "get_folder_by_id",
    "update_teacher_folder",
    "delete_teacher_folder",
    "move_folder_to_root",
    "create_collection",
    "get_collection_by_id",
    "get_collections_by_teacher",
    "update_collection",
    "delete_collection",
    "record_collection_usage",
    "move_collections_to_folder",
    "batch_delete_collections",
    "is_question_collected",
    "create_collection_tag",
    "get_collection_tags",
    "get_tag_by_id",
    "update_collection_tag",
    "delete_collection_tag",
    # 统计
    "get_collection_stats",
]
