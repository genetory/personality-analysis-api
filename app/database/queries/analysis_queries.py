from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.database import AnalysisType, Question, QuestionOption, AnalysisResult, Answer
from app.core.database import SessionLocal

class AnalysisQueries:
    """성향분석 관련 데이터베이스 쿼리 클래스"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    # AnalysisType 관련 쿼리
    def get_all_analysis_types(self) -> List[AnalysisType]:
        """모든 활성화된 성향분석 유형을 조회합니다."""
        return self.db.query(AnalysisType).filter(AnalysisType.is_active == 1).all()
    
    def get_analysis_type_by_id(self, analysis_type_id: str) -> Optional[AnalysisType]:
        """ID로 성향분석 유형을 조회합니다."""
        return self.db.query(AnalysisType).filter(AnalysisType.id == analysis_type_id).first()
    
    def create_analysis_type(self, name: str, description: str, category: str, 
                           color: str, bg_color: str) -> AnalysisType:
        """새로운 성향분석 유형을 생성합니다."""
        analysis_type = AnalysisType(
            name=name,
            description=description,
            category=category,
            color=color,
            bg_color=bg_color,
            is_active=1
        )
        self.db.add(analysis_type)
        self.db.commit()
        self.db.refresh(analysis_type)
        return analysis_type
    
    def update_analysis_type(self, analysis_type_id: str, **kwargs) -> Optional[AnalysisType]:
        """성향분석 유형을 업데이트합니다."""
        analysis_type = self.get_analysis_type_by_id(analysis_type_id)
        if analysis_type:
            for key, value in kwargs.items():
                if hasattr(analysis_type, key):
                    setattr(analysis_type, key, value)
            self.db.commit()
            self.db.refresh(analysis_type)
        return analysis_type
    
    def delete_analysis_type(self, analysis_type_id: str) -> bool:
        """성향분석 유형을 삭제합니다 (비활성화)."""
        analysis_type = self.get_analysis_type_by_id(analysis_type_id)
        if analysis_type:
            analysis_type.is_active = 0
            self.db.commit()
            return True
        return False
    
    # Question 관련 쿼리
    def get_questions_by_analysis_type(self, analysis_type_id: str) -> List[Question]:
        """특정 성향분석 유형의 질문 목록을 조회합니다."""
        return self.db.query(Question).filter(
            Question.analysis_type_id == analysis_type_id
        ).order_by(Question.order_index).all()
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """ID로 질문을 조회합니다."""
        return self.db.query(Question).filter(Question.id == question_id).first()
    
    def create_question(self, analysis_type_id: str, text: str, category: str, 
                       axis: str, order_index: int = 0) -> Question:
        """새로운 질문을 생성합니다."""
        question = Question(
            analysis_type_id=analysis_type_id,
            text=text,
            category=category,
            axis=axis,
            order_index=order_index
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question
    
    def update_question(self, question_id: str, **kwargs) -> Optional[Question]:
        """질문을 업데이트합니다."""
        question = self.get_question_by_id(question_id)
        if question:
            for key, value in kwargs.items():
                if hasattr(question, key):
                    setattr(question, key, value)
            self.db.commit()
            self.db.refresh(question)
        return question
    
    def delete_question(self, question_id: str) -> bool:
        """질문을 삭제합니다."""
        question = self.get_question_by_id(question_id)
        if question:
            self.db.delete(question)
            self.db.commit()
            return True
        return False
    
    # QuestionOption 관련 쿼리
    def get_options_by_question(self, question_id: str) -> List[QuestionOption]:
        """특정 질문의 선택지 목록을 조회합니다."""
        return self.db.query(QuestionOption).filter(
            QuestionOption.question_id == question_id
        ).order_by(QuestionOption.order_index).all()
    
    def get_option_by_id(self, option_id: str) -> Optional[QuestionOption]:
        """ID로 선택지를 조회합니다."""
        return self.db.query(QuestionOption).filter(QuestionOption.id == option_id).first()
    
    def create_question_option(self, question_id: str, text: str, value: int, 
                             axis_score: float, order_index: int = 0) -> QuestionOption:
        """새로운 질문 선택지를 생성합니다."""
        option = QuestionOption(
            question_id=question_id,
            text=text,
            value=value,
            axis_score=axis_score,
            order_index=order_index
        )
        self.db.add(option)
        self.db.commit()
        self.db.refresh(option)
        return option
    
    def update_question_option(self, option_id: str, **kwargs) -> Optional[QuestionOption]:
        """질문 선택지를 업데이트합니다."""
        option = self.get_option_by_id(option_id)
        if option:
            for key, value in kwargs.items():
                if hasattr(option, key):
                    setattr(option, key, value)
            self.db.commit()
            self.db.refresh(option)
        return option
    
    def delete_question_option(self, option_id: str) -> bool:
        """질문 선택지를 삭제합니다."""
        option = self.get_option_by_id(option_id)
        if option:
            self.db.delete(option)
            self.db.commit()
            return True
        return False
    
    # AnalysisResult 관련 쿼리
    def create_analysis_result(self, user_id: Optional[str], analysis_type_id: str,
                             empathy_score: float, active_score: float, plan_score: float,
                             express_score: float, personality_type: str, description: str,
                             recommendations: List[str] = None) -> AnalysisResult:
        """새로운 분석 결과를 생성합니다."""
        result = AnalysisResult(
            user_id=user_id,
            analysis_type_id=analysis_type_id,
            empathy_score=empathy_score,
            active_score=active_score,
            plan_score=plan_score,
            express_score=express_score,
            personality_type=personality_type,
            description=description,
            recommendations=recommendations or []
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result
    
    def get_analysis_result_by_id(self, result_id: str) -> Optional[AnalysisResult]:
        """ID로 분석 결과를 조회합니다."""
        return self.db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
    
    def get_results_by_user(self, user_id: str) -> List[AnalysisResult]:
        """특정 사용자의 모든 분석 결과를 조회합니다."""
        return self.db.query(AnalysisResult).filter(
            AnalysisResult.user_id == user_id
        ).order_by(AnalysisResult.created_at.desc()).all()
    
    def delete_analysis_result(self, result_id: str) -> bool:
        """분석 결과를 삭제합니다."""
        result = self.get_analysis_result_by_id(result_id)
        if result:
            self.db.delete(result)
            self.db.commit()
            return True
        return False
    
    # Answer 관련 쿼리
    def create_answer(self, analysis_result_id: str, question_id: str, 
                     question_option_id: str, value: int) -> Answer:
        """새로운 답변을 생성합니다."""
        answer = Answer(
            analysis_result_id=analysis_result_id,
            question_id=question_id,
            question_option_id=question_option_id,
            value=value
        )
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer
    
    def get_answers_by_result(self, result_id: str) -> List[Answer]:
        """특정 분석 결과의 모든 답변을 조회합니다."""
        return self.db.query(Answer).filter(
            Answer.analysis_result_id == result_id
        ).all()
    
    def close(self):
        """데이터베이스 연결을 종료합니다."""
        if self.db:
            self.db.close()
