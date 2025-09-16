from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.utils.uuid_utils import generate_uuid


class ResultInterpretation(Base):
    """결과 해석 모델"""
    __tablename__ = "result_interpretations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    result_type_id = Column(String(36), ForeignKey("result_types.id"), nullable=False, index=True)
    section = Column(String(50), nullable=False)  # 예: "성격 특징", "인간관계", "연애 스타일"
    content = Column(Text, nullable=False)  # 해석 내용
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    result_type = relationship("ResultType", back_populates="interpretations")
    
    def __repr__(self):
        return f"<ResultInterpretation(id={self.id}, section='{self.section}')>"
