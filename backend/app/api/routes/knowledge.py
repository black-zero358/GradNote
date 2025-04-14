from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.db.session import get_db
from app.services import knowledge as knowledge_service
from app.api.deps import get_current_user, get_current_active_user
from app.api.schemas.knowledge import (
    KnowledgePoint,
    KnowledgePointCreate,
    KnowledgePointSearch,
    KnowledgeStructure,
    MarkCreate,
    Mark,
    KnowledgeAnalyzeRequest,
    KnowledgeAnalyzeResponse,
    KnowledgeCategory,
    KnowledgeExtractRequest,
    KnowledgeExtractResponse,
    KnowledgeMarkRequest,
    KnowledgeMarkResponse,
    KnowledgePointInfo
)
from app.models.user import User
from app.models.knowledge import KnowledgePoint as KnowledgePointModel
from app.llm_services import LLMKnowledgeRetriever
from app.llm_services.knowledge_mark import KnowledgeExtractor
from app import services
from app.services import knowledge_marking

router = APIRouter()

@router.get("/structure", response_model=List[KnowledgePoint])
async def get_knowledge_points_by_structure(
    subject: str = Query(..., description="科目"),
    chapter: Optional[str] = Query(None, description="章节"),
    section: Optional[str] = Query(None, description="小节"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取最热门的知识点（根据标记次数）
    """
    return knowledge_service.get_popular_knowledge_points(db, limit)

@router.get("/subjects", response_model=List[str])
async def get_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有科目列表
    """
    return knowledge_service.get_subjects(db)

@router.get("/chapters", response_model=List[str])
async def get_chapters(
    subject: str = Query(..., description="科目名称"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定科目的所有章节
    """
    return knowledge_service.get_chapters_by_subject(db, subject)

@router.get("/sections", response_model=List[str])
async def get_sections(
    subject: str = Query(..., description="科目名称"),
    chapter: str = Query(..., description="章节名称"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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
    categories_data = await retriever.analyze_knowledge_category(
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

@router.post("/extract-from-solution", response_model=KnowledgeExtractResponse)
async def extract_knowledge_from_solution(
    request: KnowledgeExtractRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    从解题过程中提取使用的知识点，区分"已有知识点"和"新知识点"
    参数：
        question_text: 题目文本
        solution_text: 解题过程文本
        existing_knowledge_point_ids: 可选参数，如果提供，表示已知的知识点ID列表

    返回：
        existing_knowledge_points: 已存在的知识点列表
        new_knowledge_points: 新识别的知识点列表
    """
    # 初始化知识点提取器
    extractor = KnowledgeExtractor()

    # 获取可能用到的知识点
    existing_knowledge_points = []
    if request.existing_knowledge_point_ids:
        # 获取已有知识点详情
        for kp_id in request.existing_knowledge_point_ids:
            kp = knowledge_service.get_knowledge_point_by_id(db, kp_id)
            if kp:
                existing_knowledge_points.append({
                    "id": kp.id,
                    "subject": kp.subject,
                    "chapter": kp.chapter,
                    "section": kp.section,
                    "item": kp.item,
                    "details": kp.details
                })

    # 从解题过程提取知识点，等待异步方法完成
    used_existing_points, new_points = await extractor.extract_knowledge_points_from_solution(
        question_text=request.question_text,
        solution_text=request.solution_text,
        existing_knowledge_points=existing_knowledge_points
    )


    # 获取已使用的知识点完整信息
    used_existing_knowledge_points = []
    for point in used_existing_points:
        kp_id = point.get("id")
        if kp_id:
            kp = knowledge_service.get_knowledge_point_by_id(db, kp_id)
            if kp:
                used_existing_knowledge_points.append(kp)

    # 准备新识别的知识点
    new_knowledge_points = [
        KnowledgePointInfo(
            subject=point.get("subject", ""),
            chapter=point.get("chapter", ""),
            section=point.get("section", ""),
            item=point.get("item", ""),
            details=point.get("details", ""),
            is_existing=False
        )
        for point in new_points
    ]

    return KnowledgeExtractResponse(
        existing_knowledge_points=used_existing_knowledge_points,
        new_knowledge_points=new_knowledge_points
    )

@router.post("/mark-confirmed", response_model=KnowledgeMarkResponse)
async def mark_confirmed_knowledge_points(
    request: KnowledgeMarkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    处理用户确认的知识点标记，包括已有知识点和新知识点
    参数：
        question_id: 题目ID
        existing_knowledge_point_ids: 确认标记的已存在知识点ID列表
        new_knowledge_points: 确认创建的新知识点列表

    返回：
        question_id: 题目ID
        marked_knowledge_points: 已标记的所有知识点（包括新创建的）
    """
    # 处理确认的知识点标记
    new_knowledge_points_data = [kp.model_dump() for kp in request.new_knowledge_points]

    marked_points = knowledge_marking.apply_confirmed_markings(
        db=db,
        user_id=current_user.id,
        question_id=request.question_id,
        existing_knowledge_point_ids=request.existing_knowledge_point_ids,
        new_knowledge_points=new_knowledge_points_data
    )

    return KnowledgeMarkResponse(
        question_id=request.question_id,
        marked_knowledge_points=marked_points
    )