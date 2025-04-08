from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from app.api.schemas.knowledge import KnowledgePoint
from datetime import datetime

class SolveResult(BaseModel):
    question: str
    solution: str
    review_passed: Optional[bool] = None
    review_reason: Optional[str] = None
    knowledge_points: List[KnowledgePoint]
    new_knowledge_points: List[KnowledgePoint]

class SolveResponse(BaseModel):
    status: str
    message: str
    data: Optional[SolveResult] = None

class ExtractResult(BaseModel):
    status: str
    subject_info: Dict[str, Any]
    knowledge_points: List[KnowledgePoint]
    is_complete: bool
    evaluation: Dict[str, Any]

class KnowledgePointInput(BaseModel):
    id: int
    subject: str
    chapter: str
    section: str
    item: str
    details: Optional[str] = None
    mark_count: int = 0
    created_at: datetime = datetime.now()

class SolveRequest(BaseModel):
    knowledge_points: List[KnowledgePointInput] 