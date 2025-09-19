from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
import json

router = APIRouter()

@router.post("/fix-compatibility")
async def fix_compatibility(db: Session = Depends(get_db)):
    """궁합 데이터를 수정합니다 - 남성은 여성과, 여성은 남성과만 궁합"""
    try:
        # 남성 타입들의 worst를 여성 타입으로 변경
        male_updates = [
            ("에겐남-라이트", "에겐녀-하드코어"),
            ("에겐남-스탠다드", "에겐녀-라이트"),
            ("에겐남-하드코어", "에겐녀-스탠다드"),
            ("테토남-라이트", "테토녀-하드코어"),
            ("테토남-스탠다드", "테토녀-라이트"),
            ("테토남-하드코어", "테토녀-스탠다드"),
        ]
        
        # 여성 타입들의 worst를 남성 타입으로 변경
        female_updates = [
            ("에겐녀-라이트", "에겐남-하드코어"),
            ("에겐녀-스탠다드", "에겐남-라이트"),
            ("에겐녀-하드코어", "에겐남-스탠다드"),
            ("테토녀-라이트", "테토남-하드코어"),
            ("테토녀-스탠다드", "테토남-라이트"),
            ("테토녀-하드코어", "테토남-스탠다드"),
        ]
        
        all_updates = male_updates + female_updates
        
        for type_name, new_worst_type in all_updates:
            query = text("UPDATE personality_results SET compatibility_worst_type = :new_worst WHERE type_name = :type_name")
            db.execute(query, {"new_worst": new_worst_type, "type_name": type_name})
        
        db.commit()
        
        return {
            "data": {"updated_count": len(all_updates)},
            "message": "궁합 데이터가 성공적으로 수정되었습니다.",
            "code": 200
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"궁합 데이터 수정 중 오류가 발생했습니다: {str(e)}")

@router.post("/add-point-column")
async def add_point_column(db: Session = Depends(get_db)):
    """personality_results 테이블에 point 컬럼을 추가합니다"""
    try:
        # point 컬럼 추가
        query = text("ALTER TABLE personality_results ADD COLUMN point TEXT")
        db.execute(query)
        db.commit()
        
        return {
            "data": {"message": "point 컬럼이 추가되었습니다."},
            "message": "point 컬럼이 성공적으로 추가되었습니다.",
            "code": 200
        }
        
    except Exception as e:
        db.rollback()
        # 컬럼이 이미 존재하는 경우 무시
        if "Duplicate column name" in str(e):
            return {
                "data": {"message": "point 컬럼이 이미 존재합니다."},
                "message": "point 컬럼이 이미 존재합니다.",
                "code": 200
            }
        raise HTTPException(status_code=500, detail=f"point 컬럼 추가 중 오류가 발생했습니다: {str(e)}")

@router.post("/update-points")
async def update_points(db: Session = Depends(get_db)):
    """각 성격 유형의 point 데이터를 업데이트합니다"""
    try:
        points = [
            ("에겐남-라이트", "이 유형은… 약속 취소되면 바로 '그럼 나 PC방 갈게요' 하는 사람입니다 🎮"),
            ("에겐남-스탠다드", "이 유형은… 계획 따위 없이 갑자기 해외행 티켓부터 끊는 사람입니다 ✈️"),
            ("에겐남-하드코어", "이 유형은… 친구가 '야 우리 오늘 부산 가자' 했을 때 진짜 짐 싸서 따라가는 사람입니다 🎒"),
            ("에겐녀-라이트", "이 유형은… 모임에서 어색하면 먼저 '사진 찍자!' 말 꺼내는 사람입니다 📸"),
            ("에겐녀-스탠다드", "이 유형은… 단톡에서 '노래방 ㄱ?' 외치고 분위기 살리는 사람입니다 🎤"),
            ("에겐녀-하드코어", "이 유형은… 밤 10시에 갑자기 친구들 불러내서 카페 투어 시작하는 사람입니다 ☕🌙"),
            ("테토남-라이트", "이 유형은… 여행 가서 자유시간도 '2시까지 카페, 3시까지 산책' 정해두는 사람입니다 🗓️"),
            ("테토남-스탠다드", "이 유형은… 술자리 와서 안주 메뉴 고를 때도 가격대랑 양부터 따지는 사람입니다 🍺📊"),
            ("테토남-하드코어", "이 유형은… 집 앞 편의점도 네이버 지도 리뷰 보고 가는 사람입니다 📍"),
            ("테토녀-라이트", "이 유형은… 단톡 정리 담당, 스샷 찍어 공지 올려주는 사람입니다 📌"),
            ("테토녀-스탠다드", "이 유형은… 팀플 PPT 색깔·폰트까지 맞춰야 직성이 풀리는 사람입니다 🎨"),
            ("테토녀-하드코어", "이 유형은… 마트 장 보러 가서 장바구니 동선까지 계산해두는 사람입니다 🛒"),
        ]
        
        for type_name, point in points:
            query = text("UPDATE personality_results SET point = :point WHERE type_name = :type_name")
            db.execute(query, {"point": point, "type_name": type_name})
        
        db.commit()
        
        return {
            "data": {"updated_count": len(points)},
            "message": "point 데이터가 성공적으로 업데이트되었습니다.",
            "code": 200
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"point 데이터 업데이트 중 오류가 발생했습니다: {str(e)}")

@router.post("/update-analysis-type-ids")
async def update_analysis_type_ids(db: Session = Depends(get_db)):
    """모든 성격 유형의 analysis_type_id를 업데이트합니다"""
    try:
        analysis_type_id = "550e8400-e29b-41d4-a716-446655440001"  # 에겐/테토 성향분석 ID
        
        query = text("UPDATE personality_results SET analysis_type_id = :analysis_type_id")
        result = db.execute(query, {"analysis_type_id": analysis_type_id})
        
        db.commit()
        
        return {
            "data": {"updated_count": result.rowcount},
            "message": f"analysis_type_id가 성공적으로 업데이트되었습니다. ({result.rowcount}개 레코드)",
            "code": 200
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"analysis_type_id 업데이트 중 오류가 발생했습니다: {str(e)}")

@router.get("/personality-results/{id}")
async def get_personality_result_by_id(id: str, db: Session = Depends(get_db)):
    """ID로 특정 성격 유형의 결과를 가져옵니다."""
    try:
        query = text("""
        SELECT 
            id, type_name, type_title, type_description, keywords, strengths, weaknesses,
            relationships, work_style, stress_response, growth_tips,
            compatibility_best_type, compatibility_best_reason,
            compatibility_worst_type, compatibility_worst_reason,
            point, created_at, updated_at
        FROM personality_results 
        WHERE id = :id
        """)
        
        result = db.execute(query, {"id": id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Personality type not found")
        
        # 궁합 타입들의 상세 정보 가져오기
        best_type_title = ""
        worst_type_title = ""
        
        if result[11]:  # compatibility_best_type이 있는 경우
            best_query = text("SELECT type_title FROM personality_results WHERE type_name = :type_name")
            best_result = db.execute(best_query, {"type_name": result[11]}).fetchone()
            if best_result:
                best_type_title = best_result[0]
        
        if result[13]:  # compatibility_worst_type이 있는 경우
            worst_query = text("SELECT type_title FROM personality_results WHERE type_name = :type_name")
            worst_result = db.execute(worst_query, {"type_name": result[13]}).fetchone()
            if worst_result:
                worst_type_title = worst_result[0]
        
        # JSON 필드들을 파싱
        personality_result = {
            "id": result[0],
            "type_name": result[1],
            "type_title": result[2],
            "type_description": result[3],
            "keywords": json.loads(result[4]),
            "strengths": json.loads(result[5]),
            "weaknesses": json.loads(result[6]),
            "relationships": result[7],
            "work_style": result[8],
            "stress_response": result[9],
            "growth_tips": json.loads(result[10]),
            "compatibility_best_type": result[11],
            "compatibility_best_type_title": best_type_title,
            "compatibility_best_reason": result[12],
            "compatibility_worst_type": result[13],
            "compatibility_worst_type_title": worst_type_title,
            "compatibility_worst_reason": result[14],
            "point": result[15],
            "created_at": result[16].isoformat() if result[16] else None,
            "updated_at": result[17].isoformat() if result[17] else None
        }
        
        return {
            "data": personality_result,
            "message": "성격 분석 결과를 성공적으로 가져왔습니다.",
            "code": 200
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")

@router.get("/personality-results")
async def get_all_personality_results(analysis_id: str = None, db: Session = Depends(get_db)):
    """성격 유형의 결과를 가져옵니다. analysis_id가 제공되면 해당 분석의 결과만 반환합니다."""
    try:
        if analysis_id:
            query = text("""
            SELECT 
                id, type_name, type_title, type_description, keywords, strengths, weaknesses,
                relationships, work_style, stress_response, growth_tips,
                compatibility_best_type, compatibility_best_reason,
                compatibility_worst_type, compatibility_worst_reason,
                point, analysis_type_id, created_at, updated_at
            FROM personality_results 
            WHERE analysis_type_id = :analysis_id
            ORDER BY type_name
            """)
            results = db.execute(query, {"analysis_id": analysis_id}).fetchall()
        else:
            query = text("""
            SELECT 
                id, type_name, type_title, type_description, keywords, strengths, weaknesses,
                relationships, work_style, stress_response, growth_tips,
                compatibility_best_type, compatibility_best_reason,
                compatibility_worst_type, compatibility_worst_reason,
                point, analysis_type_id, created_at, updated_at
            FROM personality_results 
            ORDER BY type_name
            """)
            results = db.execute(query).fetchall()
        
        personality_results = []
        for result in results:
            # 궁합 타입들의 상세 정보 가져오기
            best_type_title = ""
            worst_type_title = ""
            
            if result[11]:  # compatibility_best_type이 있는 경우
                best_query = text("SELECT type_title FROM personality_results WHERE type_name = :type_name")
                best_result = db.execute(best_query, {"type_name": result[11]}).fetchone()
                if best_result:
                    best_type_title = best_result[0]
            
            if result[13]:  # compatibility_worst_type이 있는 경우
                worst_query = text("SELECT type_title FROM personality_results WHERE type_name = :type_name")
                worst_result = db.execute(worst_query, {"type_name": result[13]}).fetchone()
                if worst_result:
                    worst_type_title = worst_result[0]
            
            personality_result = {
                "id": result[0],
                "type_name": result[1],
                "type_title": result[2],
                "type_description": result[3],
                "keywords": json.loads(result[4]),
                "strengths": json.loads(result[5]),
                "weaknesses": json.loads(result[6]),
                "relationships": result[7],
                "work_style": result[8],
                "stress_response": result[9],
                "growth_tips": json.loads(result[10]),
                "compatibility_best_type": result[11],
                "compatibility_best_type_title": best_type_title,
                "compatibility_best_reason": result[12],
                "compatibility_worst_type": result[13],
                "compatibility_worst_type_title": worst_type_title,
                "compatibility_worst_reason": result[14],
                "point": result[15],
                "analysis_type_id": result[16],
                "created_at": result[17].isoformat() if result[17] else None,
                "updated_at": result[18].isoformat() if result[18] else None
            }
            personality_results.append(personality_result)
        
        return {
            "data": personality_results,
            "message": f"{len(personality_results)}개의 성격 분석 결과를 성공적으로 가져왔습니다.",
            "code": 200
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
