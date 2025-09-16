from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.utils.uuid_utils import generate_uuid


class Question(Base):
    """질문 모델"""
    __tablename__ = "questions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    analysis_id = Column(String(36), ForeignKey("analysis.id"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_order = Column(String(10), nullable=False, default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    analysis = relationship("Analysis", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id={self.id}, order={self.question_order}, text='{self.question_text[:50]}...')>"
