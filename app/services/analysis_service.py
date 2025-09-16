from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.analysis import Analysis
from app.models.dimension import Dimension
from app.models.question import Question
from app.models.option import Option
from app.models.option_score import OptionScore
from app.schemas.analysis import AnalysisCreate, AnalysisUpdate
from app.schemas.dimension import DimensionCreate
from app.schemas.question import QuestionCreate
from app.schemas.option import OptionCreate
from app.schemas.option_score import OptionScoreCreate


class AnalysisService:
    """성향분석 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_analysis_list(self) -> List[Analysis]:
        """모든 성향분석 유형 조회"""
        return self.db.query(Analysis).all()
    
    def get_analysis_by_id(self, analysis_id: str) -> Optional[Analysis]:
        """ID로 성향분석 조회"""
        return self.db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    def create_analysis(self, analysis_data: AnalysisCreate) -> Analysis:
        """새로운 성향분석 생성"""
        db_analysis = Analysis(**analysis_data.model_dump())
        self.db.add(db_analysis)
        self.db.commit()
        self.db.refresh(db_analysis)
        return db_analysis
    
    def update_analysis(self, analysis_id: str, analysis_data: AnalysisUpdate) -> Optional[Analysis]:
        """성향분석 업데이트"""
        db_analysis = self.get_analysis_by_id(analysis_id)
        if not db_analysis:
            return None
        
        update_data = analysis_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_analysis, field, value)
        
        self.db.commit()
        self.db.refresh(db_analysis)
        return db_analysis
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """성향분석 삭제"""
        db_analysis = self.get_analysis_by_id(analysis_id)
        if not db_analysis:
            return False
        
        self.db.delete(db_analysis)
        self.db.commit()
        return True
    
    def get_analysis_with_details(self, analysis_id: str) -> Optional[Analysis]:
        """상세 정보가 포함된 성향분석 조회"""
        return (
            self.db.query(Analysis)
            .filter(Analysis.id == analysis_id)
            .first()
        )
    
    def get_analysis_dimensions(self, analysis_id: str) -> List[Dimension]:
        """특정 분석의 성향 차원들 조회"""
        return (
            self.db.query(Dimension)
            .filter(Dimension.analysis_id == analysis_id)
            .all()
        )
    
    def get_analysis_questions(self, analysis_id: str) -> List[Question]:
        """특정 분석의 질문들 조회 (순서대로)"""
        return (
            self.db.query(Question)
            .filter(Question.analysis_id == analysis_id)
            .order_by(Question.question_order)
            .all()
        )
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """ID로 질문 조회"""
        return self.db.query(Question).filter(Question.id == question_id).first()
    
    def get_questions_with_options(self, analysis_id: str) -> List[Question]:
        """선택지가 포함된 질문들 조회"""
        from sqlalchemy.orm import joinedload
        
        return (
            self.db.query(Question)
            .options(joinedload(Question.options))
            .filter(Question.analysis_id == analysis_id)
            .order_by(Question.question_order)
            .all()
        )
    
    def create_dimension(self, dimension_data: DimensionCreate) -> Dimension:
        """새로운 성향 차원 생성"""
        db_dimension = Dimension(**dimension_data.model_dump())
        self.db.add(db_dimension)
        self.db.commit()
        self.db.refresh(db_dimension)
        return db_dimension
    
    def create_question(self, question_data: QuestionCreate) -> Question:
        """새로운 질문 생성"""
        db_question = Question(**question_data.model_dump())
        self.db.add(db_question)
        self.db.commit()
        self.db.refresh(db_question)
        return db_question
    
    def create_option(self, option_data: OptionCreate) -> Option:
        """새로운 선택지 생성"""
        db_option = Option(**option_data.model_dump())
        self.db.add(db_option)
        self.db.commit()
        self.db.refresh(db_option)
        return db_option
    
    def create_option_score(self, score_data: OptionScoreCreate) -> OptionScore:
        """새로운 선택지 점수 생성"""
        db_score = OptionScore(**score_data.model_dump())
        self.db.add(db_score)
        self.db.commit()
        self.db.refresh(db_score)
        return db_score
    
    def get_analysis_statistics(self, analysis_id: str) -> Dict[str, Any]:
        """분석 통계 정보 조회"""
        analysis = self.get_analysis_by_id(analysis_id)
        if not analysis:
            return {}
        
        dimensions_count = len(self.get_analysis_dimensions(analysis_id))
        questions_count = len(self.get_analysis_questions(analysis_id))
        
        return {
            "analysis_id": analysis_id,
            "title": analysis.title,
            "total_questions": questions_count,
            "dimensions_count": dimensions_count,
            "result_type": analysis.result_type
        }
