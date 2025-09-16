from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.services.result_service import ResultService
from app.services.analysis_service import AnalysisService
from app.schemas.result import Result, ResultWithAnalysis, UserResult

router = APIRouter()

@router.post("/submit")
async def submit_analysis_results(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """분석 결과 제출"""
    try:
        session_id = request_data.get("session_id")
        analysis_id = request_data.get("analysis_id")
        gender = request_data.get("gender")
        responses = request_data.get("responses", [])
        
        if not all([session_id, analysis_id, gender, responses]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id, analysis_id, gender, responses are required"
            )
        
        service = ResultService(db)
        result = await service.calculate_and_save_result(
            session_id=session_id,
            analysis_id=analysis_id,
            gender=gender,
            responses=responses
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/session/{session_id}", response_model=UserResult)
def get_result_by_session(session_id: str, gender: str = "female", db: Session = Depends(get_db)):
    """세션별 결과 조회 (사용자용 간소화)"""
    service = ResultService(db)
    result = service.get_result_by_session(session_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 세션의 결과를 찾을 수 없습니다."
        )
    
    # 새로운 구조에서 데이터 추출
    result_data = result.result_data or {}
    
    # 두 가지 구조 모두 지원: result_key 또는 result_type
    result_key = result_data.get("result_key") or result_data.get("result_type", "")
    # gender는 URL 파라미터에서 가져오되, result_data에 있으면 우선 사용
    result_gender = result_data.get("gender", gender)
    
    # 기본값 설정
    return UserResult(
        result_type=result_key,
        label=result_key,  # 임시로 result_key 사용 (이 필드는 UserResult 스키마의 label)
        interpretation=f"당신의 성향은 {result_key}입니다.",
        detailed_interpretation="상세 해석은 별도 API에서 조회할 수 있습니다.",
        gender=result_gender
    )


@router.get("/session/{session_id}/interpretations")
def get_sectional_interpretations(session_id: str, gender: str = "female", db: Session = Depends(get_db)):
    """세션별 섹션별 해석 조회"""
    service = ResultService(db)
    result = service.get_result_by_session(session_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 세션의 결과를 찾을 수 없습니다."
        )
    
    # 결과 데이터에서 정보 추출
    result_data = result.result_data or {}
    result_key = result_data.get("result_key") or result_data.get("result_type", "")
    result_gender = result_data.get("gender", gender)
    analysis_id = result.analysis_id
    
    # 섹션별 해석 조회
    sectional_interpretations = service.get_sectional_interpretations(analysis_id, result_key, result_gender)
    
    if not sectional_interpretations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 결과에 대한 섹션별 해석을 찾을 수 없습니다."
        )
    
    return {
        "result_type": result_key,
        "gender": result_gender,
        "interpretations": sectional_interpretations
    }


@router.get("/session/{session_id}/ai-interpretations")
def get_ai_generated_interpretations(session_id: str, gender: str = "female", db: Session = Depends(get_db)):
    """세션별 AI 생성형 섹션별 해석 조회"""
    service = ResultService(db)
    result = service.get_result_by_session(session_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 세션의 결과를 찾을 수 없습니다."
        )
    
    # 결과 데이터에서 정보 추출
    result_data = result.result_data or {}
    result_key = result_data.get("result_key") or result_data.get("result_type", "")
    result_gender = result_data.get("gender", gender)
    analysis_id = result.analysis_id
    
    # AI 생성형 해석 조회
    ai_interpretations = service.get_ai_generated_interpretations(
        session_id, analysis_id, result_key, result_gender
    )
    
    if not ai_interpretations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI 해석 생성에 실패했습니다."
        )
    
    return {
        "result_type": result_key,
        "gender": result_gender,
        "interpretations": ai_interpretations,
        "generated_by": "ai"
    }


@router.get("/analysis/{analysis_id}", response_model=List[Result])
def get_results_by_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """특정 분석의 모든 결과 조회"""
    service = ResultService(db)
    
    # 분석 존재 여부 확인
    analysis_service = AnalysisService(db)
    analysis = analysis_service.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="성향분석을 찾을 수 없습니다."
        )
    
    return service.get_results_by_analysis(analysis_id)


@router.post("/session/{session_id}/analysis/{analysis_id}", response_model=Result)
def calculate_and_save_result(
    session_id: str, 
    analysis_id: str, 
    db: Session = Depends(get_db)
):
    """응답을 기반으로 결과 계산 및 저장"""
    service = ResultService(db)
    
    # 분석 존재 여부 확인
    analysis_service = AnalysisService(db)
    analysis = analysis_service.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="성향분석을 찾을 수 없습니다."
        )
    
    result = service.calculate_and_save_result(session_id, analysis_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="응답이 완료되지 않았거나 결과 계산에 실패했습니다."
        )
    
    return result


@router.get("/analysis/{analysis_id}/statistics")
def get_result_statistics(analysis_id: str, db: Session = Depends(get_db)):
    """결과 통계 정보 조회"""
    service = ResultService(db)
    
    # 분석 존재 여부 확인
    analysis_service = AnalysisService(db)
    analysis = analysis_service.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="성향분석을 찾을 수 없습니다."
        )
    
    return service.get_result_statistics(analysis_id)
