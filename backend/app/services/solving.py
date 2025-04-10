from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models.question import WrongQuestion
from app.models.knowledge import KnowledgePoint, QuestionKnowledgeRelation
from app.llm_services.solving import LLMSolvingWorkflow
from app.services.knowledge import get_knowledge_points_by_ids, get_all_categories_csv
from app.llm_services.knowledge_retriever import LLMKnowledgeRetriever
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def solve_question(db: Session, question_id: int, knowledge_points_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    解答错题
    
    Args:
        db: 数据库会话
        question_id: 错题ID
        knowledge_points_data: 相关知识点数据列表（只包含ID）
        
    Returns:
        Dict: 解题结果，包括解题步骤和相关知识点
    """
    try:
        # 查询错题
        question = db.query(WrongQuestion).filter(WrongQuestion.id == question_id).first()
        if not question:
            return {
                "status": "error",
                "message": f"错题 ID {question_id} 不存在"
            }
        
        # 检查传入的知识点列表是否为空
        if not knowledge_points_data:
            return {
                "status": "error",
                "message": "未提供相关知识点，无法解题"
            }
        
        # 获取知识点ID列表
        knowledge_point_ids = [kp.get("id") for kp in knowledge_points_data if kp.get("id")]
        
        if not knowledge_point_ids:
            return {
                "status": "error",
                "message": "未提供有效的知识点ID，无法解题"
            }
        
        # 从数据库获取完整的知识点信息
        db_knowledge_points = get_knowledge_points_by_ids(db, knowledge_point_ids)
        
        if not db_knowledge_points:
            return {
                "status": "error",
                "message": "未找到指定的知识点，无法解题"
            }
        
        # 为LLM准备知识点数据
        llm_knowledge_points = []
        for kp in db_knowledge_points:
            llm_knowledge_points.append({
                "id": kp.id,
                "subject": kp.subject,
                "chapter": kp.chapter,
                "section": kp.section,
                "item": kp.item,
                "details": kp.details
            })
        
        # 初始化工作流状态
        initial_state = {
            "question": question.content,
            "knowledge_points": llm_knowledge_points,
            "correct_answer": question.answer,
            "attempts": 1
        }
        
        # 创建解题工作流
        workflow = LLMSolvingWorkflow()
        
        # 运行工作流
        result = workflow.invoke(initial_state)
        
        # 检查工作流是否出错
        if result.get("error"):
            return {
                "status": "error",
                "message": result.get("error", "解题过程出错")
            }
        
        # 为响应准备完整的知识点数据
        complete_knowledge_points = []
        for kp in db_knowledge_points:
            complete_knowledge_points.append({
                "id": kp.id,
                "subject": kp.subject,
                "chapter": kp.chapter,
                "section": kp.section,
                "item": kp.item,
                "details": kp.details,
                "mark_count": kp.mark_count,
                "created_at": kp.created_at
            })
        
        # 返回结果
        return {
            "status": "success",
            "message": "解题成功",
            "data": {
                "question": question.content,
                "solution": result.get("solution", ""),
                "review_passed": result.get("review_passed", False),
                "review_reason": result.get("review_reason", ""),
                "knowledge_points": complete_knowledge_points,
            }
        }
    except Exception as e:
        # 记录错误信息
        logger.error(f"解题过程出错: {str(e)}")
        
        # 返回错误信息
        return {
            "status": "error",
            "message": f"解题过程出错: {str(e)}"
        } 