from sqlalchemy import text
from app.db.session import engine
from sqlalchemy import text
from app.db.session import engine
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 允许重置序列的表白名单
ALLOWED_TABLES = {"wrong_questions", "knowledge_points", "question_knowledge_relation", "user_marks", "users"}

def reset_sequence(table_name):
    """
    重置PostgreSQL表的ID序列
    
    Args:
        table_name: 表名
    """
    if table_name not in ALLOWED_TABLES:
        logger.error(f"非法表名: {table_name}")
        return False

    try:
        with engine.connect() as connection:
            # 获取表的最大ID
            # 使用text()构建SQL，但table_name已经过白名单验证，是安全的
            result = connection.execute(text(f"SELECT MAX(id) FROM {table_name}"))
            max_id = result.scalar()
            
            if max_id is None:
                max_id = 0
                
            # 重置序列
            seq_name = f"{table_name}_id_seq"
            next_val = max_id + 1
            
            connection.execute(text(f"ALTER SEQUENCE {seq_name} RESTART WITH {next_val}"))
            connection.commit()
            
            logger.info(f"成功重置{table_name}表序列，下一个ID将是: {next_val}")
            return True
    except Exception as e:
        logger.error(f"重置序列失败: {e}")
        return False

def reset_all_sequences():
    """重置所有主要表的序列"""
    results = {}
    
    for table in ALLOWED_TABLES:
        results[table] = reset_sequence(table)
    
    return results