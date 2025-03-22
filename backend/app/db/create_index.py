from sqlalchemy import text
from app.db.session import engine
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_indexes():
    """
    创建数据库索引以提高查询性能
    """
    logger.info("开始创建数据库索引...")
    
    # 定义索引SQL语句
    indexes = [
        # 科目-章节-小节复合索引，提高结构化查询性能
        """
        CREATE INDEX IF NOT EXISTS idx_knowledge_subject_chapter_section 
        ON knowledge_points(subject, chapter, section)
        """,
        
        # 标记次数索引，提高热门知识点查询性能
        """
        CREATE INDEX IF NOT EXISTS idx_knowledge_mark_count 
        ON knowledge_points(mark_count DESC)
        """,
        
        # 错题表用户ID索引
        """
        CREATE INDEX IF NOT EXISTS idx_wrong_questions_user_id 
        ON wrong_questions(user_id)
        """,
        
        # 用户标记记录复合索引
        """
        CREATE INDEX IF NOT EXISTS idx_user_marks_user_knowledge 
        ON user_marks(user_id, knowledge_point_id)
        """
    ]
    
    # 执行索引创建
    with engine.connect() as connection:
        try:
            for index_sql in indexes:
                connection.execute(text(index_sql))
                logger.info(f"执行索引SQL: {index_sql}")
            
            # 创建向量索引
            try:
                vector_index_sql = """
                CREATE INDEX IF NOT EXISTS idx_knowledge_vector 
                ON knowledge_points USING ivfflat (vector_embedding vector_cosine_ops) WITH (lists = 100)
                """
                connection.execute(text(vector_index_sql))
                logger.info("成功创建向量索引")
            except Exception as e:
                if "operator class" in str(e).lower() or "does not exist" in str(e).lower():
                    logger.warning(f"创建向量索引失败: pgvector扩展未启用。请在PostgreSQL中运行 'CREATE EXTENSION vector;'")
                else:
                    logger.warning(f"创建向量索引失败: {e}")
            
            connection.commit()
            logger.info("所有数据库索引创建成功！")
            return True
        except Exception as e:
            connection.rollback()
            logger.error(f"创建数据库索引出错: {e}")
            return False

if __name__ == "__main__":
    # 如果直接运行此脚本，则创建索引
    create_indexes() 