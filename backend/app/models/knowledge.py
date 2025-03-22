from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base
import pgvector.sqlalchemy

class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(50), nullable=False)
    chapter = Column(String(100), nullable=False)
    section = Column(String(100), nullable=False)
    item = Column(String(100), nullable=False)
    details = Column(Text)
    mark_count = Column(Integer, default=0)
    vector_embedding = Column(pgvector.sqlalchemy.Vector(4096))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class QuestionKnowledgeRelation(Base):
    __tablename__ = "question_knowledge_relation"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"))
    question_id = Column(Integer, ForeignKey("wrong_questions.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserMark(Base):
    __tablename__ = "user_marks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"))
    question_id = Column(Integer, ForeignKey("wrong_questions.id"))
    marked_at = Column(DateTime(timezone=True), server_default=func.now()) 