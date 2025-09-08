from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

# UTF8MB4 문자셋을 위한 String 타입 설정 (MySQL에서 자동으로 처리됨)
def StringUTF8MB4(length):
    return String(length)

def TextUTF8MB4():
    return Text()

class User(Base):
    __tablename__ = "users"
    
    id = Column(CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(StringUTF8MB4(255), unique=True, index=True, nullable=False)
    name = Column(StringUTF8MB4(100), nullable=False)
    password_hash = Column(StringUTF8MB4(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    analysis_results = relationship("AnalysisResult", back_populates="user")

class AnalysisType(Base):
    __tablename__ = "analysis_types"
    
    id = Column(CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(StringUTF8MB4(100), nullable=False)
    description = Column(TextUTF8MB4(), nullable=False)
    category = Column(StringUTF8MB4(50), nullable=False)
    participants = Column(Integer, default=0)
    thumb_image_url = Column(StringUTF8MB4(500), nullable=True)
    is_active = Column(Integer, default=1)  # 0: 비활성, 1: 활성
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    questions = relationship("Question", back_populates="analysis_type")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    analysis_type_id = Column(CHAR(36), ForeignKey("analysis_types.id"), nullable=False)
    text = Column(TextUTF8MB4(), nullable=False)
    category = Column(StringUTF8MB4(50), nullable=False)  # empathy_vs_logic, active_vs_reflect, plan_vs_flow, express_vs_restrain
    axis = Column(StringUTF8MB4(20), nullable=False)  # 1, 2, 3, 4
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    analysis_type = relationship("AnalysisType", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question")
    answers = relationship("Answer", back_populates="question")

class QuestionOption(Base):
    __tablename__ = "question_options"
    
    id = Column(CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(CHAR(36), ForeignKey("questions.id"), nullable=False)
    text = Column(TextUTF8MB4(), nullable=False)
    value = Column(Integer, nullable=False)  # 1-5 scale
    axis_score = Column(Float, nullable=False)  # 해당 축에 대한 점수 (-1.0 ~ 1.0)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    question = relationship("Question", back_populates="options")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))  # UUID
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True)
    analysis_type_id = Column(CHAR(36), ForeignKey("analysis_types.id"), nullable=False)
    
    # 4축 성향 점수 (0-100)
    empathy_score = Column(Float, nullable=False)  # 에겐 vs 테토
    active_score = Column(Float, nullable=False)   # 액티브 vs 리플렉트
    plan_score = Column(Float, nullable=False)     # 플랜 vs 플로우
    express_score = Column(Float, nullable=False)  # 표현 vs 절제
    
    # 결과 정보
    personality_type = Column(StringUTF8MB4(50), nullable=False)
    description = Column(TextUTF8MB4(), nullable=False)
    recommendations = Column(JSON, nullable=True)  # JSON 배열로 저장
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    user = relationship("User", back_populates="analysis_results")
    analysis_type = relationship("AnalysisType")
    answers = relationship("Answer", back_populates="analysis_result")

class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    analysis_result_id = Column(CHAR(36), ForeignKey("analysis_results.id"), nullable=False)
    question_id = Column(CHAR(36), ForeignKey("questions.id"), nullable=False)
    question_option_id = Column(CHAR(36), ForeignKey("question_options.id"), nullable=False)
    value = Column(Integer, nullable=False)  # 1-5 scale
    
    # 관계 설정
    analysis_result = relationship("AnalysisResult", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    question_option = relationship("QuestionOption")

# PopularAnalysis는 AnalysisType으로 통합됨
