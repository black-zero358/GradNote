from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.api.schemas.solving import SolveResponse, ExtractResult
from app.services import solving as solving_service

router = APIRouter()

@router.post("/{question_id}", response_model=SolveResponse)
async def solve_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    解答错题
    
    参数:
    - question_id: 错题ID
    
    返回:
    - 解题结果，包括解题步骤和相关知识点
    """
    # 这里应该添加检查，确保用户只能解答自己的错题
    result = solving_service.solve_question(db, question_id)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result

@router.post("/extract/{question_id}", response_model=ExtractResult)
async def extract_knowledge(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    从错题中提取知识点
    
    参数:
    - question_id: 错题ID
    
    返回:
    - 提取的知识点信息
    """
    # 获取错题
    from app.models.question import WrongQuestion
    question = db.query(WrongQuestion).filter(
        WrongQuestion.id == question_id,
        WrongQuestion.user_id == current_user.id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到该错题"
        )
    
    # 调用知识点提取服务
    result = solving_service.extract_knowledge_from_question(db, question.content)
    return result 