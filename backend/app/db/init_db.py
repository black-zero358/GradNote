from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import generate_secure_password
from app.services.user import create_user, get_user_by_username
from app.api.schemas.user import UserCreate
from app.models.knowledge import KnowledgePoint
import logging
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