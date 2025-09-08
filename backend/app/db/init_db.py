from sqlalchemy.orm import Session
import os
from app.core.config import settings
from app.services.user import create_user, get_user_by_username
from app.api.schemas.user import UserCreate
from app.models.knowledge import KnowledgePoint
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从环境变量获取初始用户配置
FIRST_SUPERUSER = os.getenv("FIRST_SUPERUSER", "")
FIRST_SUPERUSER_PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD", "")
FIRST_SUPERUSER_EMAIL = os.getenv("FIRST_SUPERUSER_EMAIL", "")

# 初始知识点数据 - 简化并使用ASCII字符
INITIAL_KNOWLEDGE_POINTS = [
    {
        "subject": "Math",
        "chapter": "Calculus",
        "section": "Derivatives",
        "item": "Definition",
        "details": "The derivative of a function represents its rate of change at a specific point."
    },
    {
        "subject": "Math",
        "chapter": "Calculus",
        "section": "Derivatives",
        "item": "Geometric meaning",
        "details": "The derivative represents the slope of the tangent line at a point on the curve."
    },
    {
        "subject": "Math",
        "chapter": "Calculus",
        "section": "Integration",
        "item": "Definition",
        "details": "Integration is the process of finding the area under a curve."
    },
    {
        "subject": "Linear Algebra",
        "chapter": "Matrices",
        "section": "Operations",
        "item": "Matrix multiplication",
        "details": "Matrix multiplication C=AB requires the number of columns in A to equal the number of rows in B."
    },
    {
        "subject": "Linear Algebra",
        "chapter": "Matrices",
        "section": "Eigenvalues",
        "item": "Definition",
        "details": "Eigenvalues are special scalars associated with linear systems of equations."
    }
]

def init_db(db: Session) -> None:
    """
    初始化数据库
    """
    # 检查初始用户配置
    if not all([FIRST_SUPERUSER, FIRST_SUPERUSER_PASSWORD, FIRST_SUPERUSER_EMAIL]):
        logger.error("初始管理员用户配置不完整，请设置 FIRST_SUPERUSER、FIRST_SUPERUSER_PASSWORD 和 FIRST_SUPERUSER_EMAIL 环境变量")
        return
    
    # 创建初始管理员用户
    user = get_user_by_username(db, FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            username=FIRST_SUPERUSER,
            password=FIRST_SUPERUSER_PASSWORD,
            email=FIRST_SUPERUSER_EMAIL,
        )
        user = create_user(db, user_in)
        logger.info(f"初始用户 {FIRST_SUPERUSER} 创建成功")
    else:
        logger.info(f"用户 {FIRST_SUPERUSER} 已存在")
    
    # 创建初始知识点数据
    init_knowledge_points(db)

def init_knowledge_points(db: Session) -> None:
    """
    初始化知识点数据
    """
    existing_count = db.query(KnowledgePoint).count()
    if existing_count == 0:
        logger.info("开始添加初始知识点数据...")
        try:
            for kp_data in INITIAL_KNOWLEDGE_POINTS:
                knowledge_point = KnowledgePoint(**kp_data)
                db.add(knowledge_point)
            db.commit()
            logger.info(f"成功添加 {len(INITIAL_KNOWLEDGE_POINTS)} 条初始知识点数据")
        except Exception as e:
            db.rollback()
            logger.error(f"添加初始知识点数据失败: {e}")
    else:
        logger.info(f"数据库中已存在 {existing_count} 条知识点数据，跳过初始化") 