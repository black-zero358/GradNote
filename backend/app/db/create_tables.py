from app.db.session import Base, engine
from app.models import User, WrongQuestion, KnowledgePoint, QuestionKnowledgeRelation, UserMark
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """
    直接创建所有定义的数据库表，不使用Alembic迁移
    """
    try:
        # 创建所有定义的模型对应的表
        logger.info("开始创建数据库表...")
        Base.metadata.create_all(bind=engine)
        logger.info("所有数据库表创建成功！")
        return True
    except Exception as e:
        logger.error(f"创建数据库表出错: {e}")
        return False

if __name__ == "__main__":
    # 如果直接运行此脚本，则创建表
    create_tables() 