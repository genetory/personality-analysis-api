from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from app.models.result_type import ResultType
from app.models.result_interpretation import ResultInterpretation
from app.schemas.result_type import ResultTypeWithInterpretations


class ResultTypeService:
    """결과 타입 서비스"""
    
    # 섹션 순서 정의
    SECTION_ORDER = {
        '성격 특징': 1,
        '인간관계': 2,
        '연애 스타일': 3,
        '일상 패턴': 4,
        '강점': 5,
        '주의할 점': 6,
        '궁합': 7,
        '한 줄 정리': 8,
        '침대 위에서의 모습': 1,
        '주요 특징': 2,
        '섹스 스타일': 3,
        '섹스할 때': 4,
        '추천 체위': 5,
        '궁합': 6,
        '오늘 밤 시뮬레이션': 7,
        '한 줄 요약': 8
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_result_types_by_analysis(self, analysis_id: str) -> List[ResultType]:
        """분석 ID로 결과 타입 목록 조회"""
        return self.db.query(ResultType).filter(
            ResultType.analysis_id == analysis_id
        ).all()
    
    def get_result_type_with_interpretations(
        self, 
        analysis_id: str, 
        result_key: str, 
        gender: str
    ) -> Optional[ResultTypeWithInterpretations]:
        """결과 타입과 해석을 함께 조회 (섹션 순서 정렬)"""
        result_type = self.db.query(ResultType).options(
            joinedload(ResultType.interpretations)
        ).filter(
            and_(
                ResultType.analysis_id == analysis_id,
                ResultType.result_key == result_key,
                ResultType.gender == gender
            )
        ).first()
        
        if not result_type:
            return None
        
        # 해석을 섹션 순서에 따라 정렬
        sorted_interpretations = sorted(
            result_type.interpretations,
            key=lambda x: self.SECTION_ORDER.get(x.section, 999)
        )
        
        # 정렬된 해석으로 교체
        result_type.interpretations = sorted_interpretations
            
        return ResultTypeWithInterpretations.from_orm(result_type)
    
    def get_all_result_types_with_interpretations(
        self, 
        analysis_id: str
    ) -> List[ResultTypeWithInterpretations]:
        """분석의 모든 결과 타입과 해석을 조회 (섹션 순서 정렬)"""
        result_types = self.db.query(ResultType).options(
            joinedload(ResultType.interpretations)
        ).filter(
            ResultType.analysis_id == analysis_id
        ).all()
        
        # 각 결과 타입의 해석을 섹션 순서에 따라 정렬
        for result_type in result_types:
            sorted_interpretations = sorted(
                result_type.interpretations,
                key=lambda x: self.SECTION_ORDER.get(x.section, 999)
            )
            result_type.interpretations = sorted_interpretations
        
        return [ResultTypeWithInterpretations.from_orm(rt) for rt in result_types]
    
    def get_result_interpretations_dict(
        self, 
        analysis_id: str, 
        result_key: str, 
        gender: str
    ) -> Optional[Dict[str, str]]:
        """결과 해석을 딕셔너리 형태로 조회 (섹션 순서 정렬)"""
        result_type = self.get_result_type_with_interpretations(
            analysis_id, result_key, gender
        )
        
        if not result_type:
            return None
        
        # 해석을 섹션 순서에 따라 정렬한 후 딕셔너리로 변환
        sorted_interpretations = sorted(
            result_type.interpretations,
            key=lambda x: self.SECTION_ORDER.get(x.section, 999)
        )
        
        interpretations = {}
        for interpretation in sorted_interpretations:
            interpretations[interpretation.section] = interpretation.content
            
        return interpretations
    
    def create_result_type(
        self, 
        analysis_id: str, 
        result_key: str, 
        title: str, 
        gender: str,
        interpretations: Dict[str, str]
    ) -> ResultType:
        """결과 타입과 해석 생성"""
        # 결과 타입 생성
        result_type = ResultType(
            analysis_id=analysis_id,
            result_key=result_key,
            title=title,
            gender=gender
        )
        self.db.add(result_type)
        self.db.flush()  # ID 생성을 위해 flush
        
        # 해석 생성
        for section, content in interpretations.items():
            interpretation = ResultInterpretation(
                result_type_id=result_type.id,
                section=section,
                content=content
            )
            self.db.add(interpretation)
        
        self.db.commit()
        self.db.refresh(result_type)
        
        return result_type
