from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.utils.uuid_utils import generate_uuid


class QuestionOption(Base):
    """질문 선택지 모델"""
    __tablename__ = "question_options"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    value = Column(Integer, nullable=False)
    axis_score = Column(Float, nullable=False)
    order_index = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    question = relationship("Question", back_populates="question_options")
    
    def __repr__(self):
        return f"<QuestionOption(id={self.id}, value={self.value}, text='{self.text[:30]}...')>"
