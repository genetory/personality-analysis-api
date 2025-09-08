-- 성향분석 데이터베이스 전체 초기화 스크립트
-- 이 스크립트는 데이터베이스를 완전히 초기화합니다.

-- 1. 데이터베이스 생성 (이미 존재하면 삭제 후 재생성)
DROP DATABASE IF EXISTS `personality-analysis`;
CREATE DATABASE `personality-analysis` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 2. 데이터베이스 사용
USE `personality-analysis`;

-- 3. 테이블 생성
SOURCE create_tables.sql;

-- 4. 초기 데이터 삽입
SOURCE insert_initial_data.sql;

-- 초기화 완료 메시지
SELECT 'Database initialization completed successfully!' as message;
