from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.utils.uuid_utils import generate_uuid


class Analysis(Base):
    """성향분석 유형 모델"""
    __tablename__ = "analysis"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    total_questions = Column(String(10), nullable=False, default="0")
    result_type = Column(String(50), nullable=False)  # 'binary_pairs', 'continuous', 'categories', 'custom'
    result_config = Column(JSON, nullable=True)  # 결과 해석 규칙
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    dimensions = relationship("Dimension", back_populates="analysis", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="analysis", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="analysis")
    comments = relationship("Comment", back_populates="analysis", cascade="all, delete-orphan")
    result_types = relationship("ResultType", back_populates="analysis", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, title='{self.title}', result_type='{self.result_type}')>"
