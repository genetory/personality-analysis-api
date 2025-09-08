-- 성향분석 데이터베이스 테이블 삭제 스크립트
-- 주의: 이 스크립트는 모든 데이터를 삭제합니다!

USE `personality-analysis`;

-- 외래키 제약조건을 고려하여 역순으로 삭제
DROP TABLE IF EXISTS `answers`;
DROP TABLE IF EXISTS `analysis_results`;
DROP TABLE IF EXISTS `question_options`;
DROP TABLE IF EXISTS `questions`;
DROP TABLE IF EXISTS `analysis_types`;
DROP TABLE IF EXISTS `users`;

-- 테이블 삭제 완료 메시지
SELECT 'All tables dropped successfully!' as message;
