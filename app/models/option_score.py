from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.utils.uuid_utils import generate_uuid


class OptionScore(Base):
    """선택지별 점수 모델"""
    __tablename__ = "option_scores"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    option_id = Column(String(36), ForeignKey("options.id"), nullable=False, index=True)
    dimension_id = Column(String(36), ForeignKey("dimensions.id"), nullable=False, index=True)
    score_value = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    option = relationship("Option", back_populates="option_scores")
    dimension = relationship("Dimension", back_populates="option_scores")
    
    def __repr__(self):
        return f"<OptionScore(id={self.id}, option_id={self.option_id}, dimension_id={self.dimension_id}, score={self.score_value})>"
