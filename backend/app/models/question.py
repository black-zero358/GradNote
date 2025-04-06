from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class WrongQuestion(Base):
    __tablename__ = "wrong_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String(50), nullable=True)
    content = Column(Text, nullable=False)
    solution = Column(Text)
    answer = Column(Text)
    image_url = Column(String(255))
    remark = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 