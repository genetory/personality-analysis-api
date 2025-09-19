from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from typing import List, Dict, Any
import json
import uuid
from datetime import datetime

router = APIRouter()

def determine_burnout_level(axis_scores):
    """번아웃 단계 결정"""
    # 모든 축의 점수를 합산 (높을수록 번아웃 심각)
    total_score = sum(axis_scores.values())
    
    # 12개 질문 × 최대 5점 = 60점 만점
    # 5단계로 나누어 판정
    if total_score <= 12:  # 0-12점: 안정
        return "안정단계"
    elif total_score <= 24:  # 13-24점: 경계
        return "경계단계"
    elif total_score <= 36:  # 25-36점: 진행
        return "진행단계"
    elif total_score <= 48:  # 37-48점: 심화
        return "심화단계"
    else:  # 49-60점: 위기
        return "위기단계"

@router.post("/analyze")
async def analyze_personality(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """성격 분석 수행"""
    try:
        # 요청 데이터 추출
        analysis_id = request_data.get("analysis_id")
        gender = request_data.get("gender")
        answers = request_data.get("answers", [])
        
        if not analysis_id or not gender or not answers:
            raise HTTPException(status_code=400, detail="필수 필드가 누락되었습니다.")
        
        # 1. 질문과 선택지 정보 가져오기
        questions_query = text("""
        SELECT q.id, q.axis, qo.id as option_id, qo.axis_score
        FROM questions q
        JOIN question_options qo ON q.id = qo.question_id
        WHERE q.analysis_type_id = :analysis_id
        ORDER BY q.order_index, qo.order_index
        """)
        
        questions_result = db.execute(questions_query, {"analysis_id": analysis_id}).fetchall()
        
        if not questions_result:
            raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다.")
        
        # 2. 답변을 기반으로 점수 계산
        axis_scores = {"axis1": 0, "axis2": 0, "axis3": 0, "axis4": 0}
        
        for answer in answers:
            question_id = answer.get("question_id")
            option_id = answer.get("option_id")
            
            # 해당 선택지의 점수 찾기
            for row in questions_result:
                if row[0] == question_id and row[2] == option_id:
                    axis = row[1]  # axis (axis1, axis2, axis3, axis4)
                    score = float(row[3])  # axis_score
                    
                    if axis in axis_scores:
                        axis_scores[axis] += score
                    break
        
        # 3. 분석 타입에 따른 결과 결정
        if analysis_id == "burnout-test-001":
            # 번아웃 분석
            type_name = determine_burnout_level(axis_scores)
        else:
            # 성격 분석 (기존 로직)
            base_type = "에겐" if axis_scores["axis1"] > 0 else "테토"
            gender_suffix = "남" if gender == "male" else "녀"
            
            # 강도 계산 (axis2, axis3, axis4의 절댓값 합계)
            total_intensity = abs(axis_scores["axis2"]) + abs(axis_scores["axis3"]) + abs(axis_scores["axis4"])
            
            if total_intensity <= 2:
                intensity = "라이트"
            elif total_intensity <= 4:
                intensity = "스탠다드"
            else:
                intensity = "하드코어"
            
            type_name = f"{base_type}{gender_suffix}-{intensity}"
        
        # 4. 성격 결과 가져오기
        personality_query = text("""
        SELECT 
            id, type_name, type_title, type_description, keywords, strengths, weaknesses,
            relationships, work_style, stress_response, growth_tips,
            compatibility_best_type, compatibility_best_reason,
            compatibility_worst_type, compatibility_worst_reason,
            point, created_at, updated_at
        FROM personality_results 
        WHERE type_name = :type_name
        """)
        
        personality_result = db.execute(personality_query, {"type_name": type_name}).fetchone()
        
        if not personality_result:
            raise HTTPException(status_code=404, detail=f"성격 유형 '{type_name}'을 찾을 수 없습니다.")
        
        # 5. 분석 결과 저장
        analysis_result_id = str(uuid.uuid4())
        
        insert_query = text("""
        INSERT INTO analysis_results (
            id, analysis_type_id, user_id, personality_type, answers, scores, completed_at
        ) VALUES (
            :id, :analysis_type_id, :user_id, :personality_type, :answers, :scores, :completed_at
        )
        """)
        
        db.execute(insert_query, {
            "id": analysis_result_id,
            "analysis_type_id": analysis_id,
            "user_id": None,  # 임시로 NULL
            "personality_type": type_name,
            "answers": json.dumps(answers),
            "scores": json.dumps(axis_scores),
            "completed_at": datetime.now()
        })
        
        db.commit()
        
        # 6. 결과 반환
        return {
            "data": {
                "analysis_id": analysis_result_id,
                "gender": gender,
                "answers": answers,
                "scores": axis_scores,
                "personality_type": type_name,
                "personality_result": {
                    "id": personality_result[0],
                    "type_name": personality_result[1],
                    "type_title": personality_result[2],
                    "type_description": personality_result[3],
                    "keywords": json.loads(personality_result[4]),
                    "strengths": json.loads(personality_result[5]),
                    "weaknesses": json.loads(personality_result[6]),
                    "relationships": personality_result[7],
                    "work_style": personality_result[8],
                    "stress_response": personality_result[9],
                    "growth_tips": json.loads(personality_result[10]),
                    "compatibility_best_type": personality_result[11],
                    "compatibility_best_reason": personality_result[12],
                    "compatibility_worst_type": personality_result[13],
                    "compatibility_worst_reason": personality_result[14],
                    "point": personality_result[15],
                    "created_at": personality_result[16].isoformat() if personality_result[16] else None,
                    "updated_at": personality_result[17].isoformat() if personality_result[17] else None
                },
                "completed_at": datetime.now().isoformat()
            },
            "message": "성격 분석이 완료되었습니다.",
            "code": 200
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")

@router.get("/results/{result_id}")
async def get_analysis_result(result_id: str, db: Session = Depends(get_db)):
    """분석 결과 조회"""
    try:
        query = text("""
        SELECT id, analysis_type_id, user_id, gender, answers, scores,
               personality_type, personality_result, completed_at
        FROM analysis_results 
        WHERE id = :result_id
        """)
        
        result = db.execute(query, {"result_id": result_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
        
        return {
            "data": {
                "id": result[0],
                "analysis_type_id": result[1],
                "user_id": result[2],
                "gender": result[3],
                "answers": json.loads(result[4]),
                "scores": json.loads(result[5]),
                "personality_type": result[6],
                "personality_result": json.loads(result[7]),
                "completed_at": result[8].isoformat() if result[8] else None
            },
            "message": "분석 결과를 성공적으로 가져왔습니다.",
            "code": 200
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"결과 조회 중 오류가 발생했습니다: {str(e)}")
