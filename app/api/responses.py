from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.response_service import ResponseService
from app.services.analysis_service import AnalysisService
from app.schemas.response import Response, ResponseCreate, ResponseBatch

router = APIRouter()


@router.post("/session", response_model=dict)
def create_session(db: Session = Depends(get_db)):
    """새로운 세션 생성"""
    service = ResponseService(db)
    session_id = service.create_session_id()
    
    return {
        "session_id": session_id,
        "message": "새로운 세션이 생성되었습니다."
    }


@router.post("/", response_model=Response, status_code=status.HTTP_201_CREATED)
def create_response(response_data: ResponseCreate, db: Session = Depends(get_db)):
    """새로운 응답 생성"""
    service = ResponseService(db)
    
    # 질문과 선택지 존재 여부 확인
    analysis_service = AnalysisService(db)
    question = analysis_service.get_question_by_id(response_data.question_id)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="질문을 찾을 수 없습니다."
        )
    
    return service.create_response(response_data)


@router.post("/batch", response_model=List[Response], status_code=status.HTTP_201_CREATED)
def create_responses_batch(batch_data: ResponseBatch, db: Session = Depends(get_db)):
    """배치 응답 생성"""
    service = ResponseService(db)
    
    # 응답 데이터 검증
    if not batch_data.responses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="응답 데이터가 없습니다."
        )
    
    return service.create_responses_batch(batch_data)


@router.get("/session/{session_id}", response_model=List[Response])
def get_responses_by_session(session_id: str, db: Session = Depends(get_db)):
    """세션별 응답 조회"""
    service = ResponseService(db)
    responses = service.get_responses_by_session(session_id)
    
    if not responses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 세션의 응답을 찾을 수 없습니다."
        )
    
    return responses


@router.get("/session/{session_id}/analysis/{analysis_id}", response_model=List[Response])
def get_responses_by_analysis(
    session_id: str, 
    analysis_id: str, 
    db: Session = Depends(get_db)
):
    """특정 분석의 세션별 응답 조회"""
    service = ResponseService(db)
    
    # 분석 존재 여부 확인
    analysis_service = AnalysisService(db)
    analysis = analysis_service.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="성향분석을 찾을 수 없습니다."
        )
    
    responses = service.get_responses_by_analysis(session_id, analysis_id)
    
    if not responses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 세션의 응답을 찾을 수 없습니다."
        )
    
    return responses


@router.get("/session/{session_id}/statistics")
def get_response_statistics(session_id: str, db: Session = Depends(get_db)):
    """응답 통계 정보 조회"""
    service = ResponseService(db)
    return service.get_response_statistics(session_id)


@router.get("/session/{session_id}/analysis/{analysis_id}/scores")
def calculate_dimension_scores(
    session_id: str, 
    analysis_id: str, 
    db: Session = Depends(get_db)
):
    """성향 차원별 점수 계산"""
    service = ResponseService(db)
    
    # 분석 존재 여부 확인
    analysis_service = AnalysisService(db)
    analysis = analysis_service.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="성향분석을 찾을 수 없습니다."
        )
    
    scores = service.calculate_dimension_scores(session_id, analysis_id)
    
    if not scores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 세션의 응답을 찾을 수 없습니다."
        )
    
    return {
        "session_id": session_id,
        "analysis_id": analysis_id,
        "dimension_scores": scores
    }


@router.get("/session/{session_id}/analysis/{analysis_id}/validate")
def validate_responses_complete(
    session_id: str, 
    analysis_id: str, 
    db: Session = Depends(get_db)
):
    """응답 완료 여부 검증"""
    service = ResponseService(db)
    
    # 분석 존재 여부 확인
    analysis_service = AnalysisService(db)
    analysis = analysis_service.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="성향분석을 찾을 수 없습니다."
        )
    
    is_complete = service.validate_responses_complete(session_id, analysis_id)
    
    return {
        "session_id": session_id,
        "analysis_id": analysis_id,
        "is_complete": is_complete,
        "message": "응답이 완료되었습니다." if is_complete else "응답이 완료되지 않았습니다."
    }
