from sqlalchemy import Column, String, Text, DateTime, JSON, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.utils.uuid_utils import generate_uuid


class Analysis(Base):
    """성향분석 유형 모델"""
    __tablename__ = "analysis_types"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    total_questions = Column(Integer, nullable=False, default=12)
    estimated_time = Column(Integer, nullable=False, default=5)
    category = Column(String(50), nullable=False)
    participants = Column(Integer, nullable=False, default=0)
    thumb_image_url = Column(String(500), nullable=True)
    is_active = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    questions = relationship("Question", back_populates="analysis_type", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="analysis", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, name='{self.name}', category='{self.category}')>"
