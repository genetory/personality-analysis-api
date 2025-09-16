from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.services.result_type_service import ResultTypeService
from app.schemas.result_type import ResultType, ResultTypeWithInterpretations

router = APIRouter()


@router.get("/analysis/{analysis_id}/result-types", response_model=List[ResultType])
def get_result_types_by_analysis(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """분석의 모든 결과 타입 조회"""
    service = ResultTypeService(db)
    result_types = service.get_result_types_by_analysis(analysis_id)
    
    if not result_types:
        raise HTTPException(
            status_code=404, 
            detail="해당 분석의 결과 타입을 찾을 수 없습니다."
        )
    
    return result_types


@router.get("/analysis/{analysis_id}/result-types/{result_key}/{gender}", response_model=ResultTypeWithInterpretations)
def get_result_type_with_interpretations(
    analysis_id: str,
    result_key: str,
    gender: str,
    db: Session = Depends(get_db)
):
    """특정 결과 타입과 해석 조회"""
    service = ResultTypeService(db)
    result_type = service.get_result_type_with_interpretations(
        analysis_id, result_key, gender
    )
    
    if not result_type:
        raise HTTPException(
            status_code=404, 
            detail="해당 결과 타입을 찾을 수 없습니다."
        )
    
    return result_type


@router.get("/analysis/{analysis_id}/result-types/{result_key}/{gender}/interpretations", response_model=Dict[str, str])
def get_result_interpretations_dict(
    analysis_id: str,
    result_key: str,
    gender: str,
    db: Session = Depends(get_db)
):
    """결과 해석을 딕셔너리 형태로 조회"""
    service = ResultTypeService(db)
    interpretations = service.get_result_interpretations_dict(
        analysis_id, result_key, gender
    )
    
    if not interpretations:
        raise HTTPException(
            status_code=404, 
            detail="해당 결과 해석을 찾을 수 없습니다."
        )
    
    return interpretations


@router.get("/analysis/{analysis_id}/all-result-types", response_model=List[ResultTypeWithInterpretations])
def get_all_result_types_with_interpretations(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """분석의 모든 결과 타입과 해석을 조회"""
    service = ResultTypeService(db)
    result_types = service.get_all_result_types_with_interpretations(analysis_id)
    
    if not result_types:
        raise HTTPException(
            status_code=404, 
            detail="해당 분석의 결과 타입을 찾을 수 없습니다."
        )
    
    return result_types
