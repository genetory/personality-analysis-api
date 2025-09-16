from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
from app.models.response import Response
from app.models.option_score import OptionScore
from app.models.dimension import Dimension
from app.schemas.response import ResponseCreate, ResponseBatch


class ResponseService:
    """응답 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session_id(self) -> str:
        """새로운 세션 ID 생성"""
        return str(uuid.uuid4())
    
    def create_response(self, response_data: ResponseCreate) -> Response:
        """새로운 응답 생성"""
        db_response = Response(**response_data.model_dump())
        self.db.add(db_response)
        self.db.commit()
        self.db.refresh(db_response)
        return db_response
    
    def create_responses_batch(self, batch_data: ResponseBatch) -> List[Response]:
        """배치 응답 생성"""
        responses = []
        for response_item in batch_data.responses:
            response_data = ResponseCreate(
                session_id=batch_data.session_id,
                question_id=response_item["question_id"],
                option_id=response_item["option_id"],
                gender=batch_data.gender
            )
            db_response = Response(**response_data.model_dump())
            self.db.add(db_response)
            responses.append(db_response)
        
        self.db.commit()
        for response in responses:
            self.db.refresh(response)
        
        return responses
    
    def get_responses_by_session(self, session_id: str) -> List[Response]:
        """세션별 응답 조회"""
        return (
            self.db.query(Response)
            .filter(Response.session_id == session_id)
            .all()
        )
    
    def get_responses_by_analysis(self, session_id: str, analysis_id: str) -> List[Response]:
        """특정 분석의 세션별 응답 조회"""
        return (
            self.db.query(Response)
            .join(Response.question)
            .filter(
                Response.session_id == session_id,
                Response.question.has(analysis_id=analysis_id)
            )
            .all()
        )
    
    def calculate_dimension_scores(self, session_id: str, analysis_id: str) -> Dict[str, float]:
        """성향 차원별 점수 계산"""
        responses = self.get_responses_by_analysis(session_id, analysis_id)
        dimension_scores = {}
        
        for response in responses:
            # 선택지의 모든 점수 조회
            option_scores = (
                self.db.query(OptionScore)
                .filter(OptionScore.option_id == response.option_id)
                .all()
            )
            
            for score in option_scores:
                dimension_id = score.dimension_id
                dimension = self.db.query(Dimension).filter(Dimension.id == dimension_id).first()
                
                if dimension:
                    dimension_name = dimension.dimension_name
                    if dimension_name not in dimension_scores:
                        dimension_scores[dimension_name] = 0.0
                    dimension_scores[dimension_name] += score.score_value
        
        return dimension_scores
    
    def validate_responses_complete(self, session_id: str, analysis_id: str) -> bool:
        """응답 완료 여부 검증"""
        from app.services.analysis_service import AnalysisService
        
        analysis_service = AnalysisService(self.db)
        total_questions = len(analysis_service.get_analysis_questions(analysis_id))
        user_responses = len(self.get_responses_by_analysis(session_id, analysis_id))
        
        return user_responses >= total_questions
    
    def get_response_statistics(self, session_id: str) -> Dict[str, Any]:
        """응답 통계 정보 조회"""
        responses = self.get_responses_by_session(session_id)
        
        if not responses:
            return {"session_id": session_id, "total_responses": 0}
        
        # 분석별 응답 수 계산
        analysis_counts = {}
        for response in responses:
            analysis_id = response.question.analysis_id
            if analysis_id not in analysis_counts:
                analysis_counts[analysis_id] = 0
            analysis_counts[analysis_id] += 1
        
        return {
            "session_id": session_id,
            "total_responses": len(responses),
            "analysis_responses": analysis_counts,
            "first_response": responses[0].created_at.isoformat() if responses else None,
            "last_response": responses[-1].created_at.isoformat() if responses else None
        }
