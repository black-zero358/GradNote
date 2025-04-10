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

class SolveRequest(BaseModel):
    knowledge_points: List[int] 