from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.utils.uuid_utils import generate_uuid


class Result(Base):
    """분석 결과 모델"""
    __tablename__ = "results"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(String(36), nullable=False, index=True)  # UUID
    analysis_id = Column(String(36), ForeignKey("analysis.id"), nullable=False, index=True)
    dimension_scores = Column(JSON, nullable=False)  # 각 성향 차원별 점수
    result_data = Column(JSON, nullable=True)  # 최종 결과 데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    analysis = relationship("Analysis", back_populates="results")
    
    def __repr__(self):
        return f"<Result(id={self.id}, session_id='{self.session_id}', analysis_id={self.analysis_id})>"
