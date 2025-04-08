from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgePoint, UserMark, QuestionKnowledgeRelation
from app.models.question import WrongQuestion

def apply_confirmed_markings(
    db: Session,
    user_id: int,
    question_id: int,
    existing_knowledge_point_ids: List[int],
    new_knowledge_points: List[Dict[str, Any]]
) -> List[KnowledgePoint]:
    """
    处理用户确认的知识点标记：
    1. 对于已有知识点：增加标记次数，并与问题关联
    2. 对于新知识点：创建知识点，初始标记次数为1，并与问题关联
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        question_id: 问题ID
        existing_knowledge_point_ids: 已有知识点ID列表
        new_knowledge_points: 新知识点列表，每个包含 subject, chapter, section, item, details
        
    Returns:
        所有标记知识点的列表（包括已有和新创建的）
    """
    # 验证问题是否存在
    question = db.query(WrongQuestion).filter(WrongQuestion.id == question_id).first()
    if not question:
        raise ValueError(f"Question with ID {question_id} not found")
    
    # 处理已有知识点标记
    marked_knowledge_points = []
    for kp_id in existing_knowledge_point_ids:
        knowledge_point = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
        if knowledge_point:
            # 增加标记次数
            knowledge_point.mark_count += 1
            
            # 创建问题-知识点关联（如果不存在）
            relation = db.query(QuestionKnowledgeRelation).filter(
                QuestionKnowledgeRelation.question_id == question_id,
                QuestionKnowledgeRelation.knowledge_point_id == kp_id
            ).first()
            
            if not relation:
                relation = QuestionKnowledgeRelation(
                    question_id=question_id,
                    knowledge_point_id=kp_id
                )
                db.add(relation)
            
            # 创建用户标记记录
            user_mark = UserMark(
                user_id=user_id,
                knowledge_point_id=kp_id,
                question_id=question_id
            )
            db.add(user_mark)
            
            marked_knowledge_points.append(knowledge_point)
    
    # 处理新知识点
    for new_kp_data in new_knowledge_points:
        # 检查是否已存在相同的知识点（防止重复创建）
        existing_kp = db.query(KnowledgePoint).filter(
            KnowledgePoint.subject == new_kp_data["subject"],
            KnowledgePoint.chapter == new_kp_data["chapter"],
            KnowledgePoint.section == new_kp_data["section"],
            KnowledgePoint.item == new_kp_data["item"]
        ).first()
        
        if existing_kp:
            # 如果存在相同的知识点，使用已有的并增加标记次数
            existing_kp.mark_count += 1
            knowledge_point = existing_kp
        else:
            # 创建新知识点
            knowledge_point = KnowledgePoint(
                subject=new_kp_data["subject"],
                chapter=new_kp_data["chapter"],
                section=new_kp_data["section"],
                item=new_kp_data["item"],
                details=new_kp_data.get("details"),
                mark_count=1  # 初始标记次数为1
            )
            db.add(knowledge_point)
            db.flush()  # 获取新创建的ID
        
        # 创建问题-知识点关联
        relation = QuestionKnowledgeRelation(
            question_id=question_id,
            knowledge_point_id=knowledge_point.id
        )
        db.add(relation)
        
        # 创建用户标记记录
        user_mark = UserMark(
            user_id=user_id,
            knowledge_point_id=knowledge_point.id,
            question_id=question_id
        )
        db.add(user_mark)
        
        marked_knowledge_points.append(knowledge_point)
    
    # 提交事务
    db.commit()
    
    return marked_knowledge_points

def get_related_knowledge_points(db: Session, question_id: int) -> List[KnowledgePoint]:
    """
    获取与问题关联的所有知识点
    
    Args:
        db: 数据库会话
        question_id: 问题ID
        
    Returns:
        关联的知识点列表
    """
    # 通过关联表查询知识点
    related_points = (
        db.query(KnowledgePoint)
        .join(QuestionKnowledgeRelation, QuestionKnowledgeRelation.knowledge_point_id == KnowledgePoint.id)
        .filter(QuestionKnowledgeRelation.question_id == question_id)
        .all()
    )
    
    return related_points 