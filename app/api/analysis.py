from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import Analysis, AnalysisCreate, AnalysisUpdate, AnalysisWithDetails
from app.schemas.question import QuestionWithOptions

router = APIRouter()


@router.get("/", response_model=List[Analysis])
def get_analysis_list(db: Session = Depends(get_db)):
    """모든 성향분석 유형 조회"""
    service = AnalysisService(db)
    analyses = service.get_analysis_list()
    
    # SQLAlchemy 모델을 Pydantic 스키마로 변환
    return [
        Analysis(
            id=analysis.id,
            name=analysis.name,
            description=analysis.description,
            total_questions=analysis.total_questions,
            estimated_time=analysis.estimated_time,
            category=analysis.category,
            participants=analysis.participants,
            thumb_image_url=analysis.thumb_image_url,
            is_active=analysis.is_active,
            created_at=analysis.created_at,
            updated_at=analysis.updated_at
        ) for analysis in analyses
    ]


@router.get("/{analysis_id}", response_model=AnalysisWithDetails)
def get_analysis_by_id(analysis_id: str, db: Session = Depends(get_db)):
    """특정 성향분석 유형 조회"""
    service = AnalysisService(db)
    analysis = service.get_analysis_with_details(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="성향분석을 찾을 수 없습니다."
        )
    
    return analysis


@router.post("/", response_model=Analysis, status_code=status.HTTP_201_CREATED)
def create_analysis(analysis_data: AnalysisCreate, db: Session = Depends(get_db)):
    """새로운 성향분석 유형 생성"""
    service = AnalysisService(db)
    return service.create_analysis(analysis_data)


@router.put("/{analysis_id}", response_model=Analysis)
def update_analysis(
    analysis_id: str, 
    analysis_data: AnalysisUpdate, 
    db: Session = Depends(get_db)
):
    """성향분석 유형 업데이트"""
    service = AnalysisService(db)
    analysis = service.update_analysis(analysis_id, analysis_data)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="성향분석을 찾을 수 없습니다."
        )
    
    return analysis


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """성향분석 유형 삭제"""
    service = AnalysisService(db)
    success = service.delete_analysis(analysis_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="성향분석을 찾을 수 없습니다."
        )




@router.get("/{analysis_id}/questions", response_model=List[QuestionWithOptions])
def get_analysis_questions(analysis_id: str, db: Session = Depends(get_db)):
    """특정 분석의 질문들 조회 (선택지 포함, 순서대로)"""
    service = AnalysisService(db)
    
    # 분석 존재 여부 확인
    analysis = service.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="성향분석을 찾을 수 없습니다."
        )
    
    questions = service.get_questions_with_options(analysis_id)
    
    # 수동으로 선택지 매핑
    result = []
    for question in questions:
        question_dict = {
            "id": question.id,
            "analysis_type_id": question.analysis_type_id,
            "text": question.text,
            "category": question.category,
            "axis": question.axis,
            "order_index": question.order_index,
            "created_at": question.created_at,
            "options": [
                {
                    "id": option.id,
                    "question_id": option.question_id,
                    "text": option.text,
                    "value": option.value,
                    "axis_score": option.axis_score,
                    "order_index": option.order_index,
                    "created_at": option.created_at
                } for option in question.question_options
            ]
        }
        result.append(question_dict)
    
    return result


@router.get("/{analysis_id}/statistics")
def get_analysis_statistics(analysis_id: str, db: Session = Depends(get_db)):
    """분석 통계 정보 조회"""
    service = AnalysisService(db)
    
    # 분석 존재 여부 확인
    analysis = service.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="성향분석을 찾을 수 없습니다."
        )
    
    return service.get_analysis_statistics(analysis_id)
