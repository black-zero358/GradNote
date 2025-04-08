from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict
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
    
    model_config = ConfigDict(from_attributes=True)

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
    
    model_config = ConfigDict(from_attributes=True)

class KnowledgePointWithRelation(KnowledgePoint):
    relation_id: int
    question_id: int

# 新增的Schema类，用于题目知识点分析
class KnowledgeAnalyzeRequest(BaseModel):
    question_text: str

class KnowledgeCategory(BaseModel):
    subject: str
    chapter: str
    section: str

class KnowledgeAnalyzeResponse(BaseModel):
    categories: List[KnowledgeCategory]

# 用于从解题过程中提取知识点的Schema
class KnowledgePointInfo(BaseModel):
    subject: str
    chapter: str
    section: str
    item: str
    details: Optional[str] = None
    is_existing: bool = False  # 标记是否为已存在的知识点

class KnowledgeExtractRequest(BaseModel):
    question_text: str
    solution_text: str
    # 可选参数，如果提供，表示已知的知识点ID列表
    existing_knowledge_point_ids: Optional[List[int]] = None

class KnowledgeExtractResponse(BaseModel):
    existing_knowledge_points: List[KnowledgePoint] = []  # 已存在的知识点
    new_knowledge_points: List[KnowledgePointInfo] = []   # 新识别的知识点

# 用于确认知识点标记的Schema
class KnowledgeMarkRequest(BaseModel):
    question_id: int
    # 确认标记的已存在知识点ID列表
    existing_knowledge_point_ids: List[int] = []
    # 确认创建的新知识点列表
    new_knowledge_points: List[KnowledgePointInfo] = []

class KnowledgeMarkResponse(BaseModel):
    question_id: int
    marked_knowledge_points: List[KnowledgePoint]  # 已标记的所有知识点（包括新创建的）
