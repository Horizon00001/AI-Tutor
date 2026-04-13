from services.database.connection import get_db_connection


def init_db():
    """初始化所有数据库表"""
    from services.database.user import init_user_table
    from services.database.exam import init_exam_table
    from services.database.question import init_question_table
    from services.database.similar import init_similar_table
    from services.database.collection import init_collection_tables

    init_user_table()
    init_exam_table()
    init_question_table()
    init_similar_table()
    init_collection_tables()
