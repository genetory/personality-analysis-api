from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Comment(Base):
    """댓글 모델"""
    __tablename__ = "comments"

    id = Column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    analysis_id = Column(String(36), ForeignKey('analysis_types.id'), nullable=False, index=True)
    nickname = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 별점
    likes = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # 관계 설정
    analysis = relationship("Analysis", back_populates="comments")
