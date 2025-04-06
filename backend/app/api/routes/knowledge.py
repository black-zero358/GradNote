from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.db.session import get_db
from app.services import knowledge as knowledge_service
from app.api.deps import get_current_user
from app.api.schemas.knowledge import (
    KnowledgePoint, 
    KnowledgePointCreate,
    KnowledgePointSearch,
    KnowledgeStructure,
    MarkCreate,
    Mark,
    KnowledgeAnalyzeRequest,
    KnowledgeAnalyzeResponse,
    KnowledgeCategory
)
from app.models.user import User
from app.models.knowledge import KnowledgePoint as KnowledgePointModel
from app.llm_services import LLMKnowledgeRetriever

router = APIRouter()

@router.get("/structure", response_model=List[KnowledgePoint])
async def get_knowledge_points_by_structure(
    subject: str = Query(..., description="科目"),
    chapter: Optional[str] = Query(None, description="章节"),
    section: Optional[str] = Query(None, description="小节"),
    db: Session = Depends(get_db)
):
    """
    基于结构化信息（科目、章节、小节）查询知识点
    """
    knowledge_points = knowledge_service.get_knowledge_points_by_structure(
        db=db,
        subject=subject,
        chapter=chapter,
        section=section
    )
    return knowledge_points

@router.get("/search", response_model=List[KnowledgePoint])
async def search_knowledge_points(
    subject: Optional[str] = Query(None, description="科目"),
    chapter: Optional[str] = Query(None, description="章节"),
    section: Optional[str] = Query(None, description="小节"),
    item: Optional[str] = Query(None, description="知识点名称（支持模糊搜索）"),
    sort_by: Optional[str] = Query(None, description="排序字段，例如：mark_count, created_at"),
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="返回的最大记录数"),
    db: Session = Depends(get_db)
):
    """
    按条件搜索知识点
    """
    params = {
        "subject": subject,
        "chapter": chapter,
        "section": section,
        "item": item,
        "sort_by": sort_by
    }
    return knowledge_service.get_knowledge_points_by_params(db, params, skip, limit)

@router.get("/popular", response_model=List[KnowledgePoint])
async def get_popular_knowledge_points(
    limit: int = Query(10, description="返回的记录数"),
    db: Session = Depends(get_db)
):
    """
    获取最热门的知识点（根据标记次数）
    """
    return knowledge_service.get_popular_knowledge_points(db, limit)

@router.get("/subjects", response_model=List[str])
async def get_subjects(db: Session = Depends(get_db)):
    """
    获取所有科目列表
    """
    return knowledge_service.get_subjects(db)

@router.get("/chapters", response_model=List[str])
async def get_chapters(
    subject: str = Query(..., description="科目名称"),
    db: Session = Depends(get_db)
):
    """
    获取指定科目的所有章节
    """
    return knowledge_service.get_chapters_by_subject(db, subject)

@router.get("/sections", response_model=List[str])
async def get_sections(
    subject: str = Query(..., description="科目名称"),
    chapter: str = Query(..., description="章节名称"),
    db: Session = Depends(get_db)
):
    """
    获取指定科目和章节的所有小节
    """
    return knowledge_service.get_sections_by_chapter(db, subject, chapter)

@router.get("/user-marks", response_model=List[Mark])
async def get_user_marks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有标记
    """
    return knowledge_service.get_user_marks(db, current_user.id)

@router.get("/{knowledge_point_id}", response_model=KnowledgePoint)
async def get_knowledge_point(
    knowledge_point_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取知识点详情
    """
    knowledge_point = knowledge_service.get_knowledge_point_by_id(db, knowledge_point_id)
    if not knowledge_point:
        raise HTTPException(status_code=404, detail="知识点不存在")
    return knowledge_point

@router.post("/mark/{knowledge_point_id}", response_model=KnowledgePoint)
async def mark_knowledge_point(
    knowledge_point_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    增加知识点标记次数
    """
    knowledge_point = knowledge_service.increment_knowledge_point_mark_count(db, knowledge_point_id)
    if not knowledge_point:
        raise HTTPException(status_code=404, detail="知识点不存在")
    return knowledge_point

@router.post("/user-mark", response_model=Mark, status_code=status.HTTP_201_CREATED)
async def create_user_mark(
    mark_data: MarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建用户知识点标记记录
    """
    # 确认知识点存在
    knowledge_point = knowledge_service.get_knowledge_point_by_id(db, mark_data.knowledge_point_id)
    if not knowledge_point:
        raise HTTPException(status_code=404, detail="知识点不存在")
    
    # 创建标记
    user_mark = knowledge_service.create_user_mark(
        db=db,
        user_id=current_user.id,
        knowledge_point_id=mark_data.knowledge_point_id,
        question_id=mark_data.question_id
    )
    
    return user_mark

@router.post("/", response_model=KnowledgePoint, status_code=status.HTTP_201_CREATED)
async def create_knowledge_point(
    knowledge_point_data: KnowledgePointCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新的知识点
    """
    # 检查是否已存在相同的知识点
    existing_knowledge_point = db.query(KnowledgePointModel).filter(
        KnowledgePointModel.subject == knowledge_point_data.subject,
        KnowledgePointModel.chapter == knowledge_point_data.chapter,
        KnowledgePointModel.section == knowledge_point_data.section,
        KnowledgePointModel.item == knowledge_point_data.item
    ).first()
    
    if existing_knowledge_point:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="相同知识点已存在"
        )
    
    # 创建知识点
    return knowledge_service.create_knowledge_point(
        db=db,
        knowledge_point_data=knowledge_point_data.model_dump()
    )

@router.post("/analyze-from-question", response_model=KnowledgeAnalyzeResponse)
async def analyze_knowledge_from_question(
    request: KnowledgeAnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    分析题目文本，返回可能的知识点类别
    参数：
        question_text: 题目文本

    返回：
        categories: 知识点类别的列表

    
    """
    # 获取所有知识点类别的CSV格式
    categories_csv = knowledge_service.get_all_categories_csv(db)
    
    # 创建知识点检索器
    retriever = LLMKnowledgeRetriever()
    
    # 分析题目
    categories_data = retriever.analyze_knowledge_category(
        question_text=request.question_text,
        categories_csv=categories_csv
    )
    
    # 转换为响应格式
    categories = [
        KnowledgeCategory(
            subject=cat["subject"],
            chapter=cat["chapter"],
            section=cat["section"]
        )
        for cat in categories_data
    ]
    
    return KnowledgeAnalyzeResponse(
        categories=categories,

    ) 