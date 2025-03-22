from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.db.session import get_db
from app.services import knowledge as knowledge_service
from app.api.deps import get_current_user
from app.api.schemas.knowledge import (
    KnowledgePoint, 
    KnowledgePointCreate,
    KnowledgePointSearch,
    KnowledgeStructure
)
from app.models.user import User

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