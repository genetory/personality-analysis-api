from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.utils.uuid_utils import generate_uuid


class Dimension(Base):
    """성향 차원 모델"""
    __tablename__ = "dimensions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    analysis_id = Column(String(36), ForeignKey("analysis.id"), nullable=False, index=True)
    dimension_name = Column(String(100), nullable=False)
    dimension_description = Column(Text, nullable=True)
    dimension_type = Column(String(50), nullable=False)  # 'binary', 'continuous', 'category'
    min_value = Column(Float, nullable=True)  # 최소값 (연속형용)
    max_value = Column(Float, nullable=True)  # 최대값 (연속형용)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    analysis = relationship("Analysis", back_populates="dimensions")
    option_scores = relationship("OptionScore", back_populates="dimension")
    
    def __repr__(self):
        return f"<Dimension(id={self.id}, name='{self.dimension_name}', type='{self.dimension_type}')>"
