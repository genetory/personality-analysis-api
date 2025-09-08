from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# MySQL 데이터베이스 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # SQL 쿼리 로그 출력 (개발 시에만)
    pool_pre_ping=True,  # 연결 상태 확인
    pool_recycle=300,  # 연결 재사용 시간 (5분)
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성 (모델들이 상속받을 클래스)
Base = declarative_base()

# 데이터베이스 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
