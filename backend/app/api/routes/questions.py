from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.question import WrongQuestion
from app.api.schemas.question import Question, QuestionCreate, QuestionUpdate

router = APIRouter()

@router.post("/", response_model=Question)
async def create_question(
    question_in: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新错题"""
    db_question = WrongQuestion(
        user_id=current_user.id,
        content=question_in.content,
        solution=question_in.solution,
        remarks=question_in.remarks,
        image_url=question_in.image_url
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

@router.get("/", response_model=List[Question])
async def read_questions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的错题列表"""
    questions = db.query(WrongQuestion).filter(
        WrongQuestion.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return questions

@router.get("/{question_id}", response_model=Question)
async def read_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取特定错题详情"""
    question = db.query(WrongQuestion).filter(
        WrongQuestion.id == question_id,
        WrongQuestion.user_id == current_user.id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到该错题"
        )
    
    return question

@router.put("/{question_id}", response_model=Question)
async def update_question(
    question_id: int,
    question_in: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新错题"""
    question = db.query(WrongQuestion).filter(
        WrongQuestion.id == question_id,
        WrongQuestion.user_id == current_user.id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到该错题"
        )
    
    # 更新字段
    for field, value in question_in.dict(exclude_unset=True).items():
        setattr(question, field, value)
    
    db.commit()
    db.refresh(question)
    return question

@router.delete("/{question_id}", response_model=Question)
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除错题"""
    question = db.query(WrongQuestion).filter(
        WrongQuestion.id == question_id,
        WrongQuestion.user_id == current_user.id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到该错题"
        )
    
    db.delete(question)
    db.commit()
    return question

@router.post("/image", response_model=str)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """上传错题图片"""
    # 这里只是一个占位实现，实际需要处理文件上传和存储
    # 并且调用VLM提取文本
    return "image_url_placeholder" 