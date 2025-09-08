from typing import List, Optional
from app.models.database import AnalysisType, Question, QuestionOption, Answer, AnalysisResult
from app.database.query_manager import QueryManager
from datetime import datetime
import uuid

class AnalysisService:
    def __init__(self):
        self.query_manager = QueryManager()
    
    def get_analysis_types(self) -> List[AnalysisType]:
        """활성화된 성향분석 유형 목록을 반환합니다."""
        return self.query_manager.analysis.get_all_analysis_types()
    
    def get_questions_by_analysis_type(self, analysis_type_id: str) -> List[Question]:
        """특정 성향분석 유형의 질문 목록을 반환합니다."""
        return self.query_manager.analysis.get_questions_by_analysis_type(analysis_type_id)
    
    def get_question_options(self, question_id: str) -> List[QuestionOption]:
        """특정 질문의 선택지 목록을 반환합니다."""
        return self.query_manager.analysis.get_options_by_question(question_id)
    
    def analyze_personality(self, answers: List[dict], analysis_type_id: str, user_id: Optional[str] = None) -> AnalysisResult:
        """사용자의 답변을 바탕으로 성향분석을 수행합니다. (익명 사용자 지원)"""
        # 답변 검증
        if not answers or len(answers) == 0:
            raise ValueError("답변이 필요합니다.")
        
        # 점수 계산
        scores = self._calculate_scores(answers)
        
        # 성격 유형 결정
        personality_type = self._determine_personality_type(scores)
        
        # 설명과 추천사항 생성
        description = self._get_personality_description(personality_type)
        recommendations = self._get_recommendations(scores)
        
        # 결과 생성 및 저장 (user_id가 None이면 익명 사용자)
        result = self.query_manager.analysis.create_analysis_result(
            user_id=user_id,  # None이면 익명 사용자
            analysis_type_id=analysis_type_id,
            empathy_score=scores["empathy"],
            active_score=scores["active"],
            plan_score=scores["plan"],
            express_score=scores["express"],
            personality_type=personality_type,
            description=description,
            recommendations=recommendations
        )
        
        # 답변 저장
        for answer_data in answers:
            self.query_manager.analysis.create_answer(
                analysis_result_id=result.id,
                question_id=answer_data["question_id"],
                question_option_id=answer_data["question_option_id"],
                value=answer_data["value"]
            )
        
        return result
    
    def _calculate_scores(self, answers: List[dict]) -> dict:
        """답변을 바탕으로 4축 점수를 계산합니다."""
        scores = {
            "empathy": 0,
            "active": 0,
            "plan": 0,
            "express": 0
        }
        
        # 답변을 축별로 그룹화하여 점수 계산
        for answer_data in answers:
            question = self.query_manager.analysis.get_question_by_id(answer_data["question_id"])
            if question:
                category = question.category
                if category in scores:
                    scores[category] += answer_data["value"]
        
        # 각 축별로 평균 계산 (4개 질문씩)
        for category in scores:
            scores[category] = round(scores[category] / 4, 1)
        
        return scores
    
    def _determine_personality_type(self, scores: dict) -> str:
        """점수를 바탕으로 주요 성격 유형을 결정합니다."""
        # 간단한 로직으로 성격 유형 결정
        return "균형잡힌"
    
    def _get_personality_description(self, personality_type: str) -> str:
        """성격 유형에 따른 설명을 반환합니다."""
        return "당신의 성향분석 결과입니다."
    
    def _get_recommendations(self, scores: dict) -> List[str]:
        """점수를 바탕으로 개인화된 추천사항을 생성합니다."""
        return ["추천사항 1", "추천사항 2"]
    
    def get_analysis_result(self, result_id: str) -> Optional[AnalysisResult]:
        """특정 성향분석 결과를 조회합니다."""
        return self.query_manager.analysis.get_analysis_result_by_id(result_id)
    
    def get_anonymous_results_stats(self) -> dict:
        """익명 사용자들의 성향분석 결과 통계를 조회합니다."""
        from datetime import datetime, timedelta
        
        # 전체 익명 결과 수
        total_count = self.query_manager.result.get_anonymous_result_count()
        
        # 최근 30일간의 익명 결과 수
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_results = self.query_manager.result.get_anonymous_results_by_date_range(
            thirty_days_ago, datetime.now()
        )
        recent_count = len(recent_results)
        
        # 인기 있는 성격 유형 (전체 익명 결과에서)
        anonymous_results = self.query_manager.result.get_results_by_user(None, limit=1000)  # 최대 1000개만 조회
        personality_types = {}
        for result in anonymous_results:
            pt = result.personality_type
            personality_types[pt] = personality_types.get(pt, 0) + 1
        
        popular_types = sorted(personality_types.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_anonymous_results": total_count,
            "recent_anonymous_results": recent_count,
            "popular_personality_types": [{"type": pt, "count": count} for pt, count in popular_types]
        }
    
    def __del__(self):
        """소멸자에서 데이터베이스 연결 종료"""
        if hasattr(self, 'query_manager'):
            self.query_manager.close()
