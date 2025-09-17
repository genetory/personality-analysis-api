from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.utils.uuid_utils import generate_uuid


class Question(Base):
    """질문 모델"""
    __tablename__ = "questions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    analysis_type_id = Column(String(36), ForeignKey("analysis_types.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    axis = Column(String(20), nullable=False)
    order_index = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    analysis_type = relationship("Analysis", back_populates="questions")
    question_options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id={self.id}, order={self.order_index}, text='{self.text[:50]}...')>"
