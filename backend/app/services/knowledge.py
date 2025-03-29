from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.knowledge import KnowledgePoint, UserMark
from datetime import datetime

def get_knowledge_points_by_structure(
    db: Session,
    subject: str,
    chapter: Optional[str] = None,
    section: Optional[str] = None
) -> List[KnowledgePoint]:
    """
    基于结构化信息（科目、章节、小节）查询知识点

    Parameters:
    - db: 数据库会话
    - subject: 科目
    - chapter: 章节（可选）
    - section: 小节（可选）

    Returns:
    - 知识点列表
    """
    query = db.query(KnowledgePoint).filter(KnowledgePoint.subject == subject)
    
    if chapter:
        query = query.filter(KnowledgePoint.chapter == chapter)
    
    if section:
        query = query.filter(KnowledgePoint.section == section)
    
    return query.all()

def get_knowledge_point_by_id(db: Session, knowledge_point_id: int) -> Optional[KnowledgePoint]:
    """
    根据ID获取知识点

    Parameters:
    - db: 数据库会话
    - knowledge_point_id: 知识点ID

    Returns:
    - 知识点对象，如果不存在则返回None
    """
    return db.query(KnowledgePoint).filter(KnowledgePoint.id == knowledge_point_id).first()

def get_popular_knowledge_points(db: Session, limit: int = 10) -> List[KnowledgePoint]:
    """
    获取最热门的知识点（根据标记次数）

    Parameters:
    - db: 数据库会话
    - limit: 返回的知识点数量限制

    Returns:
    - 热门知识点列表
    """
    return db.query(KnowledgePoint).order_by(KnowledgePoint.mark_count.desc()).limit(limit).all()

def get_knowledge_points_by_params(
    db: Session,
    params: Dict[str, Any],
    skip: int = 0,
    limit: int = 100
) -> List[KnowledgePoint]:
    """
    通用知识点查询函数，支持多种查询参数

    Parameters:
    - db: 数据库会话
    - params: 查询参数字典
    - skip: 跳过的记录数
    - limit: 返回的知识点数量限制

    Returns:
    - 知识点列表
    """
    query = db.query(KnowledgePoint)
    
    # 添加过滤条件
    if "subject" in params and params["subject"]:
        query = query.filter(KnowledgePoint.subject == params["subject"])
    
    if "chapter" in params and params["chapter"]:
        query = query.filter(KnowledgePoint.chapter == params["chapter"])
    
    if "section" in params and params["section"]:
        query = query.filter(KnowledgePoint.section == params["section"])
        
    if "item" in params and params["item"]:
        query = query.filter(KnowledgePoint.item.ilike(f"%{params['item']}%"))
    
    # 添加排序
    if "sort_by" in params:
        if params["sort_by"] == "mark_count":
            query = query.order_by(KnowledgePoint.mark_count.desc())
        elif params["sort_by"] == "created_at":
            query = query.order_by(KnowledgePoint.created_at.desc())
    
    return query.offset(skip).limit(limit).all()

def get_subjects(db: Session) -> List[str]:
    """
    获取所有科目列表

    Parameters:
    - db: 数据库会话

    Returns:
    - 科目列表
    """
    return [row[0] for row in db.query(KnowledgePoint.subject).distinct().all()]

def get_chapters_by_subject(db: Session, subject: str) -> List[str]:
    """
    获取指定科目的所有章节

    Parameters:
    - db: 数据库会话
    - subject: 科目名称

    Returns:
    - 章节列表
    """
    return [
        row[0] for row in db.query(KnowledgePoint.chapter)
        .filter(KnowledgePoint.subject == subject)
        .distinct()
        .all()
    ]

def get_sections_by_chapter(db: Session, subject: str, chapter: str) -> List[str]:
    """
    获取指定科目和章节的所有小节

    Parameters:
    - db: 数据库会话
    - subject: 科目名称
    - chapter: 章节名称

    Returns:
    - 小节列表
    """
    return [
        row[0] for row in db.query(KnowledgePoint.section)
        .filter(KnowledgePoint.subject == subject)
        .filter(KnowledgePoint.chapter == chapter)
        .distinct()
        .all()
    ]

def increment_knowledge_point_mark_count(db: Session, knowledge_point_id: int) -> Optional[KnowledgePoint]:
    """
    增加知识点的标记次数

    Parameters:
    - db: 数据库会话
    - knowledge_point_id: 知识点ID

    Returns:
    - 更新后的知识点对象，如果不存在则返回None
    """
    knowledge_point = get_knowledge_point_by_id(db, knowledge_point_id)
    if knowledge_point:
        knowledge_point.mark_count += 1
        db.commit()
        db.refresh(knowledge_point)
        return knowledge_point
    return None

def create_user_mark(
    db: Session, 
    user_id: int, 
    knowledge_point_id: int, 
    question_id: int
) -> UserMark:
    """
    创建用户知识点标记记录

    Parameters:
    - db: 数据库会话
    - user_id: 用户ID
    - knowledge_point_id: 知识点ID
    - question_id: 相关错题ID

    Returns:
    - 创建的用户标记记录
    """
    # 检查标记是否已存在
    existing_mark = db.query(UserMark).filter(
        UserMark.user_id == user_id,
        UserMark.knowledge_point_id == knowledge_point_id,
        UserMark.question_id == question_id
    ).first()
    
    if existing_mark:
        return existing_mark
    
    # 创建新标记
    mark = UserMark(
        user_id=user_id,
        knowledge_point_id=knowledge_point_id,
        question_id=question_id,
        marked_at=datetime.now()
    )
    
    # 增加知识点标记计数
    knowledge_point = get_knowledge_point_by_id(db, knowledge_point_id)
    if knowledge_point:
        knowledge_point.mark_count += 1
    
    db.add(mark)
    db.commit()
    db.refresh(mark)
    return mark

def get_user_marks(db: Session, user_id: int) -> List[UserMark]:
    """
    获取用户的所有标记

    Parameters:
    - db: 数据库会话
    - user_id: 用户ID

    Returns:
    - 用户标记列表
    """
    return db.query(UserMark).filter(UserMark.user_id == user_id).all()

def create_knowledge_point(
    db: Session,
    knowledge_point_data: Dict[str, Any]
) -> KnowledgePoint:
    """
    创建新的知识点

    Parameters:
    - db: 数据库会话
    - knowledge_point_data: 知识点数据字典
    
    Returns:
    - 创建的知识点对象
    """
    knowledge_point = KnowledgePoint(
        subject=knowledge_point_data["subject"],
        chapter=knowledge_point_data["chapter"],
        section=knowledge_point_data["section"],
        item=knowledge_point_data["item"],
        details=knowledge_point_data.get("details"),
        mark_count=0
    )
    
    db.add(knowledge_point)
    db.commit()
    db.refresh(knowledge_point)
    return knowledge_point 