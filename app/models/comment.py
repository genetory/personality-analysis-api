from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.utils.uuid_utils import generate_uuid


class Comment(Base):
    """댓글 모델"""
    __tablename__ = "comments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    analysis_id = Column(String(36), ForeignKey("analysis.id"), nullable=False, index=True)
    nickname = Column(String(50), nullable=False)  # 익명 닉네임
    content = Column(Text, nullable=False)  # 댓글 내용
    rating = Column(Integer, nullable=True)  # 별점 (1-5)
    likes = Column(Integer, default=0)  # 좋아요 수
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    analysis = relationship("Analysis", back_populates="comments")
