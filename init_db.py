"""
데이터베이스 초기화 스크립트
MySQL 데이터베이스에 테이블을 생성하고 초기 데이터를 삽입합니다.
"""

from sqlalchemy import create_engine
from app.core.config import settings
from app.models.database import Base, AnalysisType, Question, QuestionOption
from app.core.database import SessionLocal

def create_tables():
    """데이터베이스 테이블을 생성합니다."""
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 테이블이 생성되었습니다.")

def insert_initial_data():
    """초기 데이터 삽입 (현재는 비어있음)"""
    print("📝 초기 데이터 삽입을 건너뜁니다.")
    print("💡 필요시 별도로 데이터를 추가하세요.")

def main():
    """메인 함수"""
    print("🚀 데이터베이스 초기화를 시작합니다...")
    print(f"📊 데이터베이스: {settings.MYSQL_DATABASE}")
    print(f"🔗 연결 URL: {settings.DATABASE_URL}")
    
    try:
        # 테이블 생성
        create_tables()
        
        # 초기 데이터 삽입
        insert_initial_data()
        
        print("✅ 데이터베이스 초기화가 완료되었습니다!")
        
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 중 오류 발생: {e}")
        print("💡 MySQL 서버가 실행 중인지 확인하고, 데이터베이스가 생성되었는지 확인해주세요.")

if __name__ == "__main__":
    main()
