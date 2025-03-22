from pydantic import BaseModel
from typing import Optional, List
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

class KnowledgePoint(KnowledgePointBase):
    id: int
    mark_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

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