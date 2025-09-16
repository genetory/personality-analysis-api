"""
데이터베이스 초기화 스크립트
테이블 생성 및 초기 데이터 삽입
"""

from sqlalchemy import create_engine
from app.core.config import settings
from app.core.database import Base
from app.models import *  # 모든 모델 import
import json


def create_tables():
    """데이터베이스 테이블 생성"""
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 테이블이 생성되었습니다.")


def insert_initial_data():
    """초기 데이터 삽입"""
    from sqlalchemy.orm import sessionmaker
    from app.models.analysis import Analysis
    from app.models.dimension import Dimension
    from app.models.question import Question
    from app.models.option import Option
    from app.models.option_score import OptionScore
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # MBTI 분석 데이터 생성
        mbti_analysis = Analysis(
            title="MBTI 성격 유형 분석",
            description="Myers-Briggs Type Indicator를 기반으로 한 성격 유형 분석",
            total_questions="4",
            result_type="binary_pairs",
            result_config={
                "binary_pairs": {
                    "E/I": {"E": "외향성", "I": "내향성"},
                    "S/N": {"S": "감각", "N": "직관"},
                    "T/F": {"T": "사고", "F": "감정"},
                    "J/P": {"J": "판단", "P": "인식"}
                },
                "interpretations": {
                    "ENFP": "열정적이고 창의적인 활동가",
                    "INTJ": "전략적이고 독립적인 건축가",
                    "ESFJ": "따뜻하고 책임감 있는 집정관",
                    "ISTP": "실용적이고 유연한 만능재주꾼"
                }
            }
        )
        db.add(mbti_analysis)
        db.commit()
        db.refresh(mbti_analysis)
        
        # MBTI 차원 생성
        dimensions_data = [
            {"name": "E/I", "description": "외향성/내향성", "type": "binary"},
            {"name": "S/N", "description": "감각/직관", "type": "binary"},
            {"name": "T/F", "description": "사고/감정", "type": "binary"},
            {"name": "J/P", "description": "판단/인식", "type": "binary"}
        ]
        
        dimensions = []
        for dim_data in dimensions_data:
            dimension = Dimension(
                analysis_id=mbti_analysis.id,
                dimension_name=dim_data["name"],
                dimension_description=dim_data["description"],
                dimension_type=dim_data["type"]
            )
            db.add(dimension)
            dimensions.append(dimension)
        
        db.commit()
        for dim in dimensions:
            db.refresh(dim)
        
        # MBTI 질문 생성
        questions_data = [
            {
                "text": "새로운 사람들과 만나는 것을 즐긴다",
                "order": "1",
                "options": [
                    {"text": "매우 그렇다", "scores": {"E/I": 2}},
                    {"text": "그렇다", "scores": {"E/I": 1}},
                    {"text": "보통이다", "scores": {"E/I": 0}},
                    {"text": "아니다", "scores": {"E/I": -1}},
                    {"text": "전혀 아니다", "scores": {"E/I": -2}}
                ]
            },
            {
                "text": "구체적인 사실보다는 가능성에 더 관심이 있다",
                "order": "2",
                "options": [
                    {"text": "매우 그렇다", "scores": {"S/N": -2}},
                    {"text": "그렇다", "scores": {"S/N": -1}},
                    {"text": "보통이다", "scores": {"S/N": 0}},
                    {"text": "아니다", "scores": {"S/N": 1}},
                    {"text": "전혀 아니다", "scores": {"S/N": 2}}
                ]
            },
            {
                "text": "논리적 분석보다는 사람들의 감정을 더 중요하게 생각한다",
                "order": "3",
                "options": [
                    {"text": "매우 그렇다", "scores": {"T/F": -2}},
                    {"text": "그렇다", "scores": {"T/F": -1}},
                    {"text": "보통이다", "scores": {"T/F": 0}},
                    {"text": "아니다", "scores": {"T/F": 1}},
                    {"text": "전혀 아니다", "scores": {"T/F": 2}}
                ]
            },
            {
                "text": "계획을 세우고 체계적으로 일하는 것을 선호한다",
                "order": "4",
                "options": [
                    {"text": "매우 그렇다", "scores": {"J/P": 2}},
                    {"text": "그렇다", "scores": {"J/P": 1}},
                    {"text": "보통이다", "scores": {"J/P": 0}},
                    {"text": "아니다", "scores": {"J/P": -1}},
                    {"text": "전혀 아니다", "scores": {"J/P": -2}}
                ]
            }
        ]
        
        for q_data in questions_data:
            question = Question(
                analysis_id=mbti_analysis.id,
                question_text=q_data["text"],
                question_order=q_data["order"]
            )
            db.add(question)
            db.commit()
            db.refresh(question)
            
            # 선택지와 점수 생성
            for opt_data in q_data["options"]:
                option = Option(
                    question_id=question.id,
                    option_text=opt_data["text"]
                )
                db.add(option)
                db.commit()
                db.refresh(option)
                
                # 점수 생성
                for dim_name, score in opt_data["scores"].items():
                    dimension = next(d for d in dimensions if d.dimension_name == dim_name)
                    option_score = OptionScore(
                        option_id=option.id,
                        dimension_id=dimension.id,
                        score_value=score
                    )
                    db.add(option_score)
            
            db.commit()
        
        print("✅ 초기 데이터가 삽입되었습니다.")
        
    except Exception as e:
        print(f"❌ 초기 데이터 삽입 중 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """메인 함수"""
    print("🚀 데이터베이스 초기화를 시작합니다...")
    
    try:
        # 테이블 생성
        create_tables()
        
        # 초기 데이터 삽입
        insert_initial_data()
        
        print("🎉 데이터베이스 초기화가 완료되었습니다!")
        
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 중 오류 발생: {e}")


if __name__ == "__main__":
    main()
