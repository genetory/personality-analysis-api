from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.result import Result
from app.models.analysis import Analysis
from app.models.dimension import Dimension
from app.models.result_type import ResultType
from app.models.result_interpretation import ResultInterpretation
from app.schemas.result import ResultCreate, ResultUpdate
from app.services.response_service import ResponseService
from app.services.ai_interpretation_service import AIIntepretationService


class ResultService:
    """결과 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.response_service = ResponseService(db)
        self.ai_interpretation_service = AIIntepretationService(db)
    
    def get_result_by_session(self, session_id: str) -> Optional[Result]:
        """세션별 결과 조회"""
        return (
            self.db.query(Result)
            .filter(Result.session_id == session_id)
            .first()
        )
    
    def get_results_by_analysis(self, analysis_id: str) -> List[Result]:
        """특정 분석의 모든 결과 조회"""
        return (
            self.db.query(Result)
            .filter(Result.analysis_id == analysis_id)
            .all()
        )
    
    def create_result(self, result_data: ResultCreate) -> Result:
        """새로운 결과 생성"""
        db_result = Result(**result_data.model_dump())
        self.db.add(db_result)
        self.db.commit()
        self.db.refresh(db_result)
        return db_result
    
    def update_result(self, session_id: str, result_data: ResultUpdate) -> Optional[Result]:
        """결과 업데이트"""
        db_result = self.get_result_by_session(session_id)
        if not db_result:
            return None
        
        update_data = result_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_result, field, value)
        
        self.db.commit()
        self.db.refresh(db_result)
        return db_result
    
    def calculate_and_save_result(self, session_id: str, analysis_id: str) -> Optional[Result]:
        """응답을 기반으로 결과 계산 및 저장"""
        # 응답 완료 여부 검증
        if not self.response_service.validate_responses_complete(session_id, analysis_id):
            return None
        
        # 기존 결과가 있는지 확인
        existing_result = self.get_result_by_session(session_id)
        if existing_result:
            return existing_result
        
        # 응답에서 성별 정보 가져오기
        responses = self.response_service.get_responses_by_analysis(session_id, analysis_id)
        gender = "male"  # 기본값
        if responses and responses[0].gender:
            gender = responses[0].gender
        
        # 차원별 점수 계산
        dimension_scores = self.response_service.calculate_dimension_scores(session_id, analysis_id)
        
        # 분석 정보 조회
        analysis = self.db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return None
        
        # 결과 데이터 생성
        result_data = self._generate_result_data(analysis, dimension_scores, gender)
        
        # 결과 저장
        result_create = ResultCreate(
            session_id=session_id,
            analysis_id=analysis_id,
            dimension_scores=dimension_scores,
            result_data=result_data
        )
        
        return self.create_result(result_create)
    
    def _generate_result_data(self, analysis: Analysis, dimension_scores: Dict[str, float], gender: str = "male") -> Dict[str, Any]:
        """분석 타입에 따른 결과 데이터 생성"""
        result_type = analysis.result_type
        result_config = analysis.result_config or {}
        
        if result_type == "binary_pairs":
            return self._generate_binary_pairs_result(dimension_scores, result_config, gender)
        elif result_type == "continuous":
            return self._generate_continuous_result(dimension_scores, result_config)
        elif result_type == "categories":
            return self._generate_categories_result(dimension_scores, result_config)
        elif result_type == "custom":
            return self._generate_custom_result(dimension_scores, result_config, gender)
        else:
            return {"error": "Unknown result type"}
    
    def _generate_binary_pairs_result(self, dimension_scores: Dict[str, float], config: Dict[str, Any], gender: str = "male") -> Dict[str, Any]:
        """이분법 결과 생성 (MBTI 스타일)"""
        # Egen/Teto 32유형 테스트의 경우
        if "binary_axes" in config:
            return self._generate_egen_teto_result(dimension_scores, config, gender)
        
        result_type = ""
        detailed_scores = {}
        
        for dimension_name, score in dimension_scores.items():
            if "/" in dimension_name:  # E/I, S/N 형태
                parts = dimension_name.split("/")
                if len(parts) == 2:
                    if score > 0:
                        result_type += parts[0]
                        detailed_scores[dimension_name] = {
                            "score": score,
                            "type": parts[0],
                            "description": config.get("binary_pairs", {}).get(dimension_name, {}).get(parts[0], parts[0])
                        }
                    else:
                        result_type += parts[1]
                        detailed_scores[dimension_name] = {
                            "score": score,
                            "type": parts[1],
                            "description": config.get("binary_pairs", {}).get(dimension_name, {}).get(parts[1], parts[1])
                        }
        
        return {
            "result_key": result_type,  # result_key로 변경
            "result_type": result_type,
            "detailed_scores": detailed_scores,
            "interpretation": config.get("interpretations", {}).get(result_type, "분석 결과를 확인해주세요."),
            "gender": gender  # 성별 정보 추가
        }
    
    def _generate_continuous_result(self, dimension_scores: Dict[str, float], config: Dict[str, Any]) -> Dict[str, Any]:
        """연속형 결과 생성 (빅파이브 스타일)"""
        detailed_scores = {}
        ranges = config.get("ranges", [
            {"min": 0, "max": 30, "label": "낮음"},
            {"min": 31, "max": 70, "label": "보통"},
            {"min": 71, "max": 100, "label": "높음"}
        ])
        
        for dimension_name, score in dimension_scores.items():
            level = self._get_level_from_ranges(score, ranges)
            detailed_scores[dimension_name] = {
                "score": score,
                "level": level,
                "description": config.get("descriptions", {}).get(dimension_name, dimension_name)
            }
        
        return {
            "detailed_scores": detailed_scores,
            "overall_assessment": self._generate_overall_assessment(detailed_scores, config)
        }
    
    def _generate_categories_result(self, dimension_scores: Dict[str, float], config: Dict[str, Any]) -> Dict[str, Any]:
        """카테고리 결과 생성"""
        threshold = config.get("threshold", 0.6)
        max_categories = config.get("max_categories", 2)
        
        # 점수를 정규화 (0-1 범위)
        total_score = sum(abs(score) for score in dimension_scores.values())
        normalized_scores = {}
        
        for dimension_name, score in dimension_scores.items():
            if total_score > 0:
                normalized_scores[dimension_name] = abs(score) / total_score
            else:
                normalized_scores[dimension_name] = 0
        
        # 임계값 이상인 카테고리들 선택
        selected_categories = [
            {"name": name, "score": score}
            for name, score in normalized_scores.items()
            if score >= threshold
        ]
        
        # 점수 순으로 정렬하고 최대 개수만큼 선택
        selected_categories.sort(key=lambda x: x["score"], reverse=True)
        selected_categories = selected_categories[:max_categories]
        
        return {
            "selected_categories": selected_categories,
            "all_scores": normalized_scores,
            "threshold": threshold
        }
    
    def _generate_custom_result(self, dimension_scores: Dict[str, float], config: Dict[str, Any], gender: str = "male") -> Dict[str, Any]:
        """커스텀 결과 생성"""
        # Egen/Teto 32유형 테스트의 경우
        if "binary_axes" in config:
            return self._generate_egen_teto_result(dimension_scores, config, gender)
        
        return {
            "dimension_scores": dimension_scores,
            "custom_analysis": config.get("custom_analysis", {}),
            "recommendations": config.get("recommendations", [])
        }
    
    def _generate_egen_teto_result(self, dimension_scores: Dict[str, float], config: Dict[str, Any], gender: str = "male") -> Dict[str, Any]:
        """Egen/Teto 32유형 결과 생성"""
        binary_axes = config.get("binary_axes", {})
        labels = config.get("labels", {})
        
        # 각 축에서의 결과 결정
        result_parts = []
        detailed_scores = {}
        
        for axis_name, axis_config in binary_axes.items():
            score = dimension_scores.get(axis_name, 0)
            
            if score > 0:
                result_parts.append(axis_config["pos"])
                detailed_scores[axis_name] = {
                    "score": score,
                    "type": axis_config["pos"],
                    "description": f"{axis_name} 성향"
                }
            else:
                result_parts.append(axis_config["neg"])
                detailed_scores[axis_name] = {
                    "score": score,
                    "type": axis_config["neg"],
                    "description": f"{axis_name} 성향"
                }
        
        # 결과 타입 조합 (EX/RV 제외)
        result_type = "-".join([result_parts[0], result_parts[1], result_parts[3]])  # AC_RF, EG_TT, PL_FL만 사용
        
        # 성별에 따른 라벨 매핑
        gender_labels = labels.get(gender, {})
        final_title = gender_labels.get(result_type, result_type)
        
        # 상세 해석 생성 (데이터베이스에서 가져오기)
        detailed_interpretation = self._get_detailed_interpretation_from_config(result_type, gender, config)
        
        return {
            "result_key": result_type,  # result_key로 변경하여 해석 테이블과 연결
            "result_type": result_type,
            "title": final_title,
            "detailed_scores": detailed_scores,
            "dimension_scores": dimension_scores,
            "interpretation": f"당신의 성향은 {final_title}입니다.",
            "detailed_interpretation": detailed_interpretation,
            "gender": gender  # 성별 정보 추가
        }
    
    def _get_detailed_interpretation_from_config(self, result_type: str, gender: str, config: Dict[str, Any]) -> str:
        """데이터베이스에서 상세 해석 가져오기"""
        detailed_interpretations = config.get("detailed_interpretations", {})
        result_interpretations = detailed_interpretations.get(result_type, {})
        return result_interpretations.get(gender, "해당 유형에 대한 상세 해석이 준비되지 않았습니다.")
    
    def get_sectional_interpretations(self, analysis_id: str, result_type: str, gender: str) -> Optional[Dict[str, str]]:
        """섹션별 해석 조회"""
        result_type_obj = (
            self.db.query(ResultType)
            .filter(
                ResultType.analysis_id == analysis_id,
                ResultType.result_key == result_type,
                ResultType.gender == gender
            )
            .first()
        )
        
        if not result_type_obj:
            return None
        
        # 해석 조회
        interpretations = (
            self.db.query(ResultInterpretation)
            .filter(ResultInterpretation.result_type_id == result_type_obj.id)
            .all()
        )
        
        # 섹션별로 정리
        sectional_interpretations = {}
        for interpretation in interpretations:
            sectional_interpretations[interpretation.section] = interpretation.content
        
        return sectional_interpretations
    
    def get_ai_generated_interpretations(self, session_id: str, analysis_id: str, result_type: str, gender: str) -> Optional[Dict[str, str]]:
        """AI 생성형 섹션별 해석 조회"""
        try:
            # AI로 개인화된 해석 생성
            interpretations = self.ai_interpretation_service.generate_batch_interpretations(
                session_id=session_id,
                analysis_id=analysis_id,
                result_type=result_type,
                gender=gender
            )
            
            return interpretations
            
        except Exception as e:
            print(f"AI 해석 생성 실패: {e}")
            # AI 실패 시 기존 해석으로 fallback
            return self.get_sectional_interpretations(analysis_id, result_type, gender)
    
    def _get_level_from_ranges(self, score: float, ranges: List[Dict[str, Any]]) -> str:
        """점수에 따른 레벨 반환"""
        for range_item in ranges:
            if range_item["min"] <= score <= range_item["max"]:
                return range_item["label"]
        return "알 수 없음"
    
    def _generate_overall_assessment(self, detailed_scores: Dict[str, Any], config: Dict[str, Any]) -> str:
        """전체 평가 생성"""
        # 가장 높은 점수와 가장 낮은 점수 찾기
        if not detailed_scores:
            return "분석 결과가 없습니다."
        
        max_score = max(detailed_scores.values(), key=lambda x: x["score"])
        min_score = min(detailed_scores.values(), key=lambda x: x["score"])
        
        return config.get("overall_assessment", 
                         f"가장 높은 특성: {max_score['description']}, 가장 낮은 특성: {min_score['description']}")
    
    def get_result_statistics(self, analysis_id: str) -> Dict[str, Any]:
        """결과 통계 정보 조회"""
        results = self.get_results_by_analysis(analysis_id)
        
        if not results:
            return {"analysis_id": analysis_id, "total_results": 0}
        
        # 결과 타입별 통계 (binary_pairs의 경우)
        result_types = {}
        for result in results:
            if result.result_data and "result_type" in result.result_data:
                result_type = result.result_data["result_type"]
                if result_type not in result_types:
                    result_types[result_type] = 0
                result_types[result_type] += 1
        
        return {
            "analysis_id": analysis_id,
            "total_results": len(results),
            "result_types": result_types,
            "latest_result": results[-1].created_at.isoformat() if results else None
        }
    
    async def calculate_and_save_result(
        self, 
        session_id: str, 
        analysis_id: str, 
        gender: str, 
        responses: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """분석 결과 계산 및 저장"""
        try:
            # 1. 분석 정보 조회
            analysis = self.db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                raise ValueError(f"Analysis not found: {analysis_id}")
            
            # 2. 응답 저장
            saved_responses = []
            for response in responses:
                saved_response = self.response_service.create_response(
                    session_id=session_id,
                    question_id=response["question_id"],
                    option_id=response["option_id"]
                )
                saved_responses.append(saved_response)
            
            # 3. 결과 계산
            if analysis.result_type == "binary_pairs":
                result_data = self._generate_egen_teto_result(
                    analysis_id=analysis_id,
                    gender=gender,
                    responses=saved_responses
                )
            elif analysis.result_type == "continuous":
                result_data = self._generate_continuous_result(
                    analysis_id=analysis_id,
                    gender=gender,
                    responses=saved_responses
                )
            else:
                result_data = self._generate_binary_pairs_result(
                    analysis_id=analysis_id,
                    gender=gender,
                    responses=saved_responses
                )
            
            # 4. 결과 저장
            result = Result(
                session_id=session_id,
                analysis_id=analysis_id,
                dimension_scores=result_data.get("dimension_scores", {}),
                result_data=result_data
            )
            self.db.add(result)
            self.db.commit()
            
            return {
                "result_id": result.id,
                "session_id": session_id,
                "analysis_id": analysis_id,
                "result_type": result_data.get("result_type", ""),
                "title": result_data.get("title", ""),
                "description": result_data.get("description", ""),
                "is_complete": True
            }
            
        except Exception as e:
            self.db.rollback()
            raise e
