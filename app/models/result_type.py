from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.utils.uuid_utils import generate_uuid


class ResultType(Base):
    """결과 타입 모델"""
    __tablename__ = "result_types"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    analysis_id = Column(String(36), ForeignKey("analysis.id"), nullable=False, index=True)
    result_key = Column(String(100), nullable=False, index=True)  # 예: "에겐-액티브-플랜"
    title = Column(String(100), nullable=False)  # 예: "솔직한 해결사"
    subtitle = Column(String(200), nullable=True)  # 예: "문제 터지면 제일 먼저 달려가는 급발진 해결 담당"
    gender = Column(Enum('male', 'female', name='gender_enum'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    analysis = relationship("Analysis", back_populates="result_types")
    interpretations = relationship("ResultInterpretation", back_populates="result_type", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ResultType(id={self.id}, result_key='{self.result_key}', title='{self.title}', gender='{self.gender}')>"
