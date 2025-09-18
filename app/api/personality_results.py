from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
import json

router = APIRouter()

@router.get("/personality-results/{type_name}")
async def get_personality_result(type_name: str, db: Session = Depends(get_db)):
    """특정 성격 유형의 결과를 가져옵니다."""
    try:
        query = text("""
        SELECT 
            id, type_name, catchphrase, keywords, strengths, weaknesses,
            relationships, work_style, stress_response, growth_tips,
            best_compatibility_type, best_compatibility_reason,
            worst_compatibility_type, worst_compatibility_reason,
            created_at, updated_at
        FROM personality_results 
        WHERE type_name = :type_name
        """)
        
        result = db.execute(query, {"type_name": type_name}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Personality type not found")
        
        # 궁합 타입들의 정보 가져오기 (ID로 조회)
        best_type = ""
        best_catchphrase = ""
        worst_type = ""
        worst_catchphrase = ""
        
        if result[10]:  # best_compatibility_type_id가 있는 경우
            best_query = text("SELECT type_name, catchphrase FROM personality_results WHERE id = :id")
            best_result = db.execute(best_query, {"id": result[10]}).fetchone()
            if best_result:
                best_type = best_result[1]  # catchphrase 사용
                best_catchphrase = best_result[1]
        
        if result[12]:  # worst_compatibility_type_id가 있는 경우
            worst_query = text("SELECT type_name, catchphrase FROM personality_results WHERE id = :id")
            worst_result = db.execute(worst_query, {"id": result[12]}).fetchone()
            if worst_result:
                worst_type = worst_result[1]  # catchphrase 사용
                worst_catchphrase = worst_result[1]
        
        # JSON 필드들을 파싱
        personality_result = {
            "id": result[0],
            "type": result[1],
            "summary": {
                "catchphrase": result[2],
                "keywords": json.loads(result[3])
            },
            "strengths": json.loads(result[4]),
            "weaknesses": json.loads(result[5]),
            "relationships": result[6],
            "workStyle": result[7],
            "stressResponse": result[8],
            "growthTips": json.loads(result[9]),
            "compatibility": {
                "best": {
                    "type": best_type,
                    "catchphrase": best_catchphrase,
                    "reason": result[11]
                },
                "worst": {
                    "type": worst_type,
                    "catchphrase": worst_catchphrase,
                    "reason": result[13]
                }
            },
            "createdAt": result[14].isoformat() if result[14] else None,
            "updatedAt": result[15].isoformat() if result[15] else None
        }
        
        return {
            "data": personality_result,
            "message": "성격 분석 결과를 성공적으로 가져왔습니다.",
            "code": 200
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/personality-results")
async def get_all_personality_results(db: Session = Depends(get_db)):
    """모든 성격 유형의 결과를 가져옵니다."""
    try:
        query = text("""
        SELECT 
            id, type_name, catchphrase, keywords, strengths, weaknesses,
            relationships, work_style, stress_response, growth_tips,
            best_compatibility_type, best_compatibility_reason,
            worst_compatibility_type, worst_compatibility_reason,
            created_at, updated_at
        FROM personality_results 
        ORDER BY type_name
        """)
        
        results = db.execute(query).fetchall()
        
        personality_results = []
        for result in results:
            # 궁합 타입들의 정보 가져오기 (ID로 조회)
            best_type = ""
            best_catchphrase = ""
            worst_type = ""
            worst_catchphrase = ""
            
            if result[10]:  # best_compatibility_type_id가 있는 경우
                best_query = text("SELECT type_name, catchphrase FROM personality_results WHERE id = :id")
                best_result = db.execute(best_query, {"id": result[10]}).fetchone()
                if best_result:
                    best_type = best_result[1]  # catchphrase 사용
                    best_catchphrase = best_result[1]
            
            if result[12]:  # worst_compatibility_type_id가 있는 경우
                worst_query = text("SELECT type_name, catchphrase FROM personality_results WHERE id = :id")
                worst_result = db.execute(worst_query, {"id": result[12]}).fetchone()
                if worst_result:
                    worst_type = worst_result[1]  # catchphrase 사용
                    worst_catchphrase = worst_result[1]
            
            personality_result = {
                "id": result[0],
                "type": result[1],
                "summary": {
                    "catchphrase": result[2],
                    "keywords": json.loads(result[3])
                },
                "strengths": json.loads(result[4]),
                "weaknesses": json.loads(result[5]),
                "relationships": result[6],
                "workStyle": result[7],
                "stressResponse": result[8],
                "growthTips": json.loads(result[9]),
                "compatibility": {
                    "best": {
                        "type": best_type,
                        "catchphrase": best_catchphrase,
                        "reason": result[11]
                    },
                    "worst": {
                        "type": worst_type,
                        "catchphrase": worst_catchphrase,
                        "reason": result[13]
                    }
                },
                "createdAt": result[14].isoformat() if result[14] else None,
                "updatedAt": result[15].isoformat() if result[15] else None
            }
            personality_results.append(personality_result)
        
        return {
            "data": personality_results,
            "message": f"{len(personality_results)}개의 성격 분석 결과를 성공적으로 가져왔습니다.",
            "code": 200
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
