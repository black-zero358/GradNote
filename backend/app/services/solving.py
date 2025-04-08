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
        knowledge_points_data: 相关知识点数据列表
        
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
        
        # 获取完整的知识点信息，包括 mark_count 和 created_at
        complete_knowledge_points = []
        knowledge_point_ids = [kp.get("id") for kp in knowledge_points_data if kp.get("id")]
        
        if knowledge_point_ids:
            # 从数据库获取完整的知识点信息
            db_knowledge_points = get_knowledge_points_by_ids(db, knowledge_point_ids)
            
            # 创建ID到知识点的映射
            kp_map = {kp.id: kp for kp in db_knowledge_points}
            
            # 使用数据库信息补充客户端提供的知识点数据
            for kp_data in knowledge_points_data:
                kp_id = kp_data.get("id")
                if kp_id and kp_id in kp_map:
                    # 数据库中存在的知识点
                    db_kp = kp_map[kp_id]
                    complete_knowledge_points.append({
                        "id": db_kp.id,
                        "subject": db_kp.subject,
                        "chapter": db_kp.chapter,
                        "section": db_kp.section,
                        "item": db_kp.item,
                        "details": db_kp.details,
                        "mark_count": db_kp.mark_count,
                        "created_at": db_kp.created_at
                    })
                else:
                    # 数据库中不存在的知识点，添加默认值
                    complete_knowledge_points.append({
                        **kp_data,
                        "mark_count": kp_data.get("mark_count", 0),
                        "created_at": kp_data.get("created_at", datetime.now())
                    })
        else:
            # 如果没有有效的知识点ID，使用客户端提供的数据并添加默认值
            for kp_data in knowledge_points_data:
                complete_knowledge_points.append({
                    **kp_data,
                    "mark_count": kp_data.get("mark_count", 0),
                    "created_at": kp_data.get("created_at", datetime.now())
                })
        
        # 初始化工作流状态（使用原始知识点数据，因为LLM不需要mark_count和created_at字段）
        initial_state = {
            "question": question.content,
            "knowledge_points": knowledge_points_data,
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
        
        # 返回结果（使用完整的知识点数据，包含mark_count和created_at）
        return {
            "status": "success",
            "message": "解题成功",
            "data": {
                "question": question.content,
                "solution": result.get("solution", ""),
                "review_passed": result.get("review_passed", False),
                "review_reason": result.get("review_reason", ""),
                "knowledge_points": complete_knowledge_points,
                "new_knowledge_points": [] # LLM暂时无法生成新知识点，保留此项以兼容原有接口
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