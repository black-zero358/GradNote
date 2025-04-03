from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import logging
from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.question import WrongQuestion
from app.api.schemas.question import Question, QuestionCreate, QuestionUpdate, QuestionResponse
from app.services import image as image_service
from app.api.routes.image import process_image

router = APIRouter()
logger = logging.getLogger(__name__)

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
        subject=question_in.subject,
        solution=question_in.solution,
        answer=question_in.answer,
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
    
    # 更新字段，只更新非空字段
    update_data = question_in.dict(exclude_unset=True)
    # 过滤掉值为None和空字符串的字段
    update_data = {field: value for field, value in update_data.items() if value is not None and value != ""}
    
    logger.info(f"更新错题 ID: {question_id}, 用户ID: {current_user.id}, 更新字段: {update_data}")
    
    for field, value in update_data.items():
        setattr(question, field, value)
    
    db.commit()
    db.refresh(question)
    logger.info(f"错题 ID: {question_id} 更新成功")
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

@router.post("/from-image", response_model=QuestionResponse)
async def create_question_from_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    从图片创建错题
    
    此API将图片处理与错题创建结合在一起，一步完成从图片提取文本并创建错题的过程。
    
    处理流程:
    1. 上传图片
    2. 使用图像处理服务提取文本内容
    3. 将提取的文本及图片URL保存为新的错题
    
    参数:
    - file: 错题图片文件
    
    返回:
    - status: 处理状态 (success/error)
    - data: 创建的错题信息
    - message: 操作结果消息
    """
    # 检查文件类型
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持图像文件"
        )
    
    # 读取文件内容
    file_content = await file.read()
    
    # 复用图像处理API
    # 修复 UploadFile 初始化问题
    # 需要重新定位文件指针到开始位置
    await file.seek(0)
    # 直接传递已有的 file 对象而不是尝试创建新的
    result = await process_image(file=file, db=db, current_user=current_user)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    # 创建错题
    question_data = {
        "content": result["text"],
        "image_url": result["image_url"]
    }
    
    try:
        
        # 保存到数据库
        db_question = WrongQuestion(
            user_id=current_user.id,
            **question_data
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        
        # 将 SQLAlchemy 模型转换为字典，而不是直接返回模型对象
        question_dict = {
            "id": db_question.id,
            "user_id": db_question.user_id,
            "content": db_question.content,
            "solution": db_question.solution,
            "answer": db_question.answer,
            "subject": db_question.subject,
            "image_url": db_question.image_url,
            "created_at": db_question.created_at
        }
        
        return {
            "status": "success",
            "data": question_dict,
            "message": "从图片创建错题成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建错题失败: {str(e)}"
        ) 