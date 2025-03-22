import os
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from langchain.schema import Document
from app.models.question import WrongQuestion
from app.models.knowledge import KnowledgePoint, QuestionKnowledgeRelation
from app.services import knowledge as knowledge_service
from app.ml.solving import SolveWorkflow
from app.ml.knowledge_mark import KnowledgeExtractor

# 从环境变量获取API配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL")

# 初始化解题工作流和知识点提取器
solve_workflow = None
knowledge_extractor = None

def get_solve_workflow() -> SolveWorkflow:
    """获取解题工作流实例"""
    global solve_workflow
    if solve_workflow is None:
        solve_workflow = SolveWorkflow(
            api_key=OPENAI_API_KEY,
            api_base=OPENAI_API_BASE,
            model_name=OPENAI_LLM_MODEL
        )
    return solve_workflow

def get_knowledge_extractor() -> KnowledgeExtractor:
    """获取知识点提取器实例"""
    global knowledge_extractor
    if knowledge_extractor is None:
        knowledge_extractor = KnowledgeExtractor(
            api_key=OPENAI_API_KEY,
            api_base=OPENAI_API_BASE,
            model_name=OPENAI_LLM_MODEL
        )
    return knowledge_extractor

def convert_knowledge_point_to_document(knowledge_point: KnowledgePoint) -> Document:
    """将KnowledgePoint对象转换为Document对象"""
    return Document(
        page_content=knowledge_point.details or knowledge_point.item,
        metadata={
            "id": knowledge_point.id,
            "subject": knowledge_point.subject,
            "chapter": knowledge_point.chapter,
            "section": knowledge_point.section,
            "item": knowledge_point.item
        }
    )

def solve_question(db: Session, question_id: int) -> Dict:
    """
    解答错题
    
    Args:
        db: 数据库会话
        question_id: 错题ID
        
    Returns:
        解题结果字典
    """
    # 获取错题
    question = db.query(WrongQuestion).filter(WrongQuestion.id == question_id).first()
    if not question:
        return {
            "status": "error",
            "message": "找不到该错题",
            "data": None
        }
    
    # 查询关联的知识点
    relations = db.query(QuestionKnowledgeRelation).filter(
        QuestionKnowledgeRelation.question_id == question_id
    ).all()
    
    # 如果已经有解题结果，直接返回
    if question.solution:
        # 获取相关知识点
        knowledge_points = []
        for relation in relations:
            kp = knowledge_service.get_knowledge_point_by_id(db, relation.knowledge_point_id)
            if kp:
                knowledge_points.append(kp)
        
        return {
            "status": "success",
            "message": "解题结果已存在",
            "data": {
                "question": question.content,
                "solution": question.solution,
                "knowledge_points": [
                    {
                        "id": kp.id,
                        "subject": kp.subject,
                        "chapter": kp.chapter,
                        "section": kp.section,
                        "item": kp.item,
                        "details": kp.details
                    } for kp in knowledge_points
                ],
                "new_knowledge_points": []
            }
        }
    
    # 获取相关知识点
    knowledge_points = []
    for relation in relations:
        kp = knowledge_service.get_knowledge_point_by_id(db, relation.knowledge_point_id)
        if kp:
            knowledge_points.append(kp)
    
    # 将KnowledgePoint对象转换为Document对象
    knowledge_docs = [convert_knowledge_point_to_document(kp) for kp in knowledge_points]
    
    # 评估知识点是否完备
    extractor = get_knowledge_extractor()
    evaluation = extractor.evaluate_knowledge_points(knowledge_docs, question.content)
    is_complete = evaluation.get("is_complete", False) and evaluation.get("confidence", 0) >= 7
    
    # 执行解题工作流
    workflow = get_solve_workflow()
    result = workflow.solve(question.content, knowledge_docs, is_complete)
    
    # 更新题目的解答
    if result["solution"]:
        question.solution = result["solution"]
        db.commit()
    
    # 处理新提取的知识点
    new_knowledge_points = result.get("new_knowledge_points", [])
    saved_new_points = []
    
    if new_knowledge_points:
        for kp_data in new_knowledge_points:
            # 检查知识点是否已存在
            existing_kp = db.query(KnowledgePoint).filter(
                KnowledgePoint.subject == kp_data["subject"],
                KnowledgePoint.chapter == kp_data["chapter"],
                KnowledgePoint.section == kp_data["section"],
                KnowledgePoint.item == kp_data["item"]
            ).first()
            
            if existing_kp:
                # 如果已存在，检查是否已与问题关联
                relation = db.query(QuestionKnowledgeRelation).filter(
                    QuestionKnowledgeRelation.knowledge_point_id == existing_kp.id,
                    QuestionKnowledgeRelation.question_id == question_id
                ).first()
                
                if not relation:
                    # 如果未关联，创建关联
                    relation = QuestionKnowledgeRelation(
                        knowledge_point_id=existing_kp.id,
                        question_id=question_id
                    )
                    db.add(relation)
                
                saved_new_points.append(existing_kp)
            else:
                # 创建新知识点
                new_kp = KnowledgePoint(
                    subject=kp_data["subject"],
                    chapter=kp_data["chapter"],
                    section=kp_data["section"],
                    item=kp_data["item"],
                    details=kp_data.get("details", "")
                )
                db.add(new_kp)
                db.flush()  # 获取新ID
                
                # 创建关联
                relation = QuestionKnowledgeRelation(
                    knowledge_point_id=new_kp.id,
                    question_id=question_id
                )
                db.add(relation)
                saved_new_points.append(new_kp)
        
        db.commit()
    
    # 返回结果
    return {
        "status": "success",
        "message": "解题成功",
        "data": {
            "question": question.content,
            "solution": result["solution"],
            "review_passed": result.get("review_passed", False),
            "review_reason": result.get("review_reason", ""),
            "knowledge_points": [
                {
                    "id": kp.id,
                    "subject": kp.subject,
                    "chapter": kp.chapter,
                    "section": kp.section,
                    "item": kp.item,
                    "details": kp.details
                } for kp in knowledge_points
            ],
            "new_knowledge_points": [
                {
                    "id": kp.id,
                    "subject": kp.subject,
                    "chapter": kp.chapter,
                    "section": kp.section,
                    "item": kp.item,
                    "details": kp.details
                } for kp in saved_new_points
            ]
        }
    }

def extract_knowledge_from_question(db: Session, question_text: str) -> Dict:
    """
    从问题中提取知识点信息
    
    Args:
        db: 数据库会话
        question_text: 问题文本
        
    Returns:
        提取结果字典
    """
    extractor = get_knowledge_extractor()
    subject_info = extractor.extract_subject_info(question_text)
    
    # 根据置信度选择查询方式
    if subject_info.get("confidence", 0) >= 7:
        # 高置信度，使用结构化查询
        knowledge_points = knowledge_service.get_knowledge_points_by_structure(
            db,
            subject_info.get("subject", ""),
            subject_info.get("chapter", ""),
            subject_info.get("section", "")
        )
        
        # 转换为Document对象
        knowledge_docs = [convert_knowledge_point_to_document(kp) for kp in knowledge_points]
        
        # 评估知识点是否完备
        evaluation = extractor.evaluate_knowledge_points(knowledge_docs, question_text)
        is_complete = evaluation.get("is_complete", False) and evaluation.get("confidence", 0) >= 7
        
        return {
            "status": "success",
            "subject_info": subject_info,
            "knowledge_points": [
                {
                    "id": kp.id,
                    "subject": kp.subject,
                    "chapter": kp.chapter,
                    "section": kp.section,
                    "item": kp.item,
                    "details": kp.details
                } for kp in knowledge_points
            ],
            "is_complete": is_complete,
            "evaluation": evaluation
        }
    else:
        # 低置信度，返回有限信息
        return {
            "status": "partial",
            "subject_info": subject_info,
            "knowledge_points": [],
            "is_complete": False,
            "evaluation": {
                "is_complete": False,
                "confidence": 0,
                "missing_concepts": ["需要更多信息"],
                "reasoning": "题目分类置信度低"
            }
        } 