# 성향분석 API 서버

FastAPI를 사용한 성향분석 플랫폼의 백엔드 API 서버입니다.

## 기능

- **성향분석**: Big Five 모델 기반 성격 분석
- **질문 관리**: 25개 성향분석 질문 제공
- **결과 저장**: 분석 결과 저장 및 조회
- **인기 분석**: 인기 있는 성향분석 목록 제공
- **사용자 관리**: 사용자 등록, 로그인, 프로필 관리

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. MySQL 데이터베이스 설정

#### 방법 1: SQL 스크립트 사용 (권장)
```bash
# MySQL에 접속하여 스크립트 실행
mysql -u root -p < database/init_database.sql
```

#### 방법 2: 수동 설정
```sql
-- MySQL에서 데이터베이스 생성
CREATE DATABASE `personality-analysis` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 테이블 생성
SOURCE database/create_tables.sql;

-- 초기 데이터 삽입
SOURCE database/insert_initial_data.sql;
```

### 3. 환경 변수 설정

```bash
cp env.example .env
# .env 파일을 편집하여 MySQL 설정값을 수정하세요
```

### 4. Python 의존성 설치

```bash
pip install -r requirements.txt
```

### 5. 서버 실행

```bash
# 개발 모드
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 또는
python main.py
```

### 6. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 성향분석 (Analysis)

- `GET /api/v1/analysis/questions` - 질문 목록 조회
- `POST /api/v1/analysis/analyze` - 성향분석 수행
- `GET /api/v1/analysis/popular` - 인기 분석 목록
- `GET /api/v1/analysis/results/{result_id}` - 분석 결과 조회

### 사용자 (Users)

- `POST /api/v1/users/register` - 사용자 등록
- `POST /api/v1/users/login` - 사용자 로그인
- `GET /api/v1/users/profile/{user_id}` - 사용자 프로필 조회

### 결과 (Results)

- `GET /api/v1/results/user/{user_id}` - 사용자 결과 목록
- `DELETE /api/v1/results/{result_id}` - 결과 삭제

## 프로젝트 구조

```
personality-analysis-api/
├── app/
│   ├── api/           # API 라우터
│   ├── models/        # Pydantic 모델
│   ├── services/      # 비즈니스 로직
│   └── core/          # 설정 및 공통 기능
├── tests/             # 테스트 파일
├── main.py           # FastAPI 앱 진입점
├── requirements.txt  # Python 의존성
└── README.md         # 프로젝트 문서
```

## 개발 가이드

### 새로운 API 엔드포인트 추가

1. `app/models/`에 Pydantic 모델 정의
2. `app/services/`에 비즈니스 로직 구현
3. `app/api/`에 라우터 추가
4. `main.py`에 라우터 등록

### 테스트

```bash
pytest
```

## 기술 스택

- **FastAPI**: 웹 프레임워크
- **Pydantic**: 데이터 검증 및 직렬화
- **Uvicorn**: ASGI 서버
- **SQLAlchemy**: ORM (향후 추가 예정)
- **Redis**: 캐싱 (향후 추가 예정)
