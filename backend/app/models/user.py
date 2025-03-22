from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 