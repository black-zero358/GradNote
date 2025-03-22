from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class KnowledgePointBase(BaseModel):
    subject: str
    chapter: str
    section: str
    item: str
    details: Optional[str] = None

class KnowledgePointCreate(KnowledgePointBase):
    pass

class KnowledgePointUpdate(BaseModel):
    subject: Optional[str] = None
    chapter: Optional[str] = None
    section: Optional[str] = None
    item: Optional[str] = None
    details: Optional[str] = None
    mark_count: Optional[int] = None

class KnowledgePoint(KnowledgePointBase):
    id: int
    mark_count: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

class KnowledgePointSearch(BaseModel):
    subject: Optional[str] = None
    chapter: Optional[str] = None
    section: Optional[str] = None
    item: Optional[str] = None
    sort_by: Optional[str] = None
    skip: Optional[int] = 0
    limit: Optional[int] = 100

class KnowledgeStructure(BaseModel):
    subject: str
    chapter: Optional[str] = None
    section: Optional[str] = None

class MarkCreate(BaseModel):
    knowledge_point_id: int
    question_id: int

class Mark(MarkCreate):
    id: int
    user_id: int
    marked_at: datetime
    
    class Config:
        from_attributes = True

class KnowledgePointWithRelation(KnowledgePoint):
    relation_id: int
    question_id: int 