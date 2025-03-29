from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class QuestionBase(BaseModel):
    content: str
    subject: Optional[str] = None
    solution: Optional[str] = None
    remarks: Optional[str] = None

class QuestionCreate(QuestionBase):
    image_url: Optional[str] = None

class QuestionImageUpload(BaseModel):
    file_content: bytes

class QuestionUpdate(BaseModel):
    content: Optional[str] = None
    solution: Optional[str] = None
    remarks: Optional[str] = None
    image_url: Optional[str] = None

class Question(QuestionBase):
    id: int
    user_id: int
    image_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    message: Optional[str] = None 