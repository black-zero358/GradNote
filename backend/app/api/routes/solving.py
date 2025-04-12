from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.api.schemas.solving import SolveResponse, SolveRequest
from app.services import solving as solving_service

router = APIRouter()

@router.post("/{question_id}", response_model=SolveResponse)
async def solve_question(
    question_id: int,
    request_data: SolveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    解答错题
    
    参数:
    - question_id: 错题ID
    - request_data: 包含知识点ID列表的请求体
    
    返回:
    - 解题结果，包括解题步骤和相关知识点
    """
    knowledge_points_data = [{"id": kp_id} for kp_id in request_data.knowledge_points]
    
    result = await solving_service.solve_question(
        db=db, 
        question_id=question_id, 
        knowledge_points_data=knowledge_points_data
    )
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result

