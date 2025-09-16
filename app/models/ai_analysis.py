from sqlalchemy import Column, String, DateTime, Text, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from app.core.database import Base
import uuid
from datetime import datetime

class AIAnalysis(Base):
    """AI 성향 분석 세션"""
    __tablename__ = "ai_analyses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    analysis_type = Column(String(50), nullable=False)  # 'egen_teto', 'bdsm', 'custom'
    is_active = Column(Integer, default=1)  # 1: active, 0: inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    sessions = relationship("AIAnalysisSession", back_populates="analysis")

class AIAnalysisSession(Base):
    """AI 성향 분석 세션"""
    __tablename__ = "ai_analysis_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("ai_analyses.id"), nullable=False)
    session_id = Column(String(100), nullable=False, unique=True)
    gender = Column(String(10), nullable=False, default='male')  # 'male', 'female'
    status = Column(String(20), default='in_progress')  # 'in_progress', 'completed', 'abandoned'
    current_question_index = Column(Integer, default=0)
    answers = Column(JSON, default=list)  # [{"question_id": "xxx", "answer": 1}, ...]
    result_type = Column(String(100))  # 최종 결과 타입
    result_data = Column(JSON)  # 최종 결과 데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    analysis = relationship("AIAnalysis", back_populates="sessions")
    questions = relationship("AIAnalysisQuestion", back_populates="session")

class AIAnalysisQuestion(Base):
    """AI가 생성한 질문"""
    __tablename__ = "ai_analysis_questions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("ai_analysis_sessions.id"), nullable=False)
    question_index = Column(Integer, nullable=False)  # 질문 순서
    question_text = Column(Text, nullable=False)  # 질문 내용
    option_1 = Column(Text, nullable=False)  # 선택지 1
    option_2 = Column(Text, nullable=False)  # 선택지 2
    category = Column(String(50))  # 질문 카테고리 (energy, decision_making, etc.)
    ai_prompt = Column(Text)  # AI에게 보낸 프롬프트
    user_answer = Column(Integer)  # 사용자 답변 (1 or 2)
    answered_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    session = relationship("AIAnalysisSession", back_populates="questions")

class AIAnalysisResult(Base):
    """AI 성향 분석 결과"""
    __tablename__ = "ai_analysis_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("ai_analysis_sessions.id"), nullable=False)
    result_type = Column(String(100), nullable=False)  # 결과 유형
    title = Column(String(200), nullable=False)  # 결과 제목
    description = Column(Text)  # 결과 설명
    characteristics = Column(JSON)  # 특징들
    compatibility = Column(JSON)  # 궁합 정보
    recommendations = Column(JSON)  # 추천사항
    confidence_score = Column(Integer)  # AI 신뢰도 점수 (0-100)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    session = relationship("AIAnalysisSession")
