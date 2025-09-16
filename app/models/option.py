from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.utils.uuid_utils import generate_uuid


class Option(Base):
    """선택지 모델"""
    __tablename__ = "options"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False, index=True)
    option_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    question = relationship("Question", back_populates="options")
    option_scores = relationship("OptionScore", back_populates="option", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Option(id={self.id}, text='{self.option_text[:30]}...')>"
