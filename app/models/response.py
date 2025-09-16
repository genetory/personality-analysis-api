from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base
from app.utils.uuid_utils import generate_uuid


class Response(Base):
    """사용자 응답 모델"""
    __tablename__ = "responses"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(String(36), nullable=False, index=True)  # UUID
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False, index=True)
    option_id = Column(String(36), ForeignKey("options.id"), nullable=False, index=True)
    gender = Column(String(10), nullable=True)  # male/female
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    question = relationship("Question")
    option = relationship("Option")
    
    def __repr__(self):
        return f"<Response(id={self.id}, session_id='{self.session_id}', question_id={self.question_id}, option_id={self.option_id})>"
