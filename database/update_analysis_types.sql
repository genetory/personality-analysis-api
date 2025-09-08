-- AnalysisType 테이블 스키마 업데이트
-- color, bg_color 컬럼 제거하고 thumb_image_url 컬럼 추가

-- 기존 컬럼 삭제
ALTER TABLE analysis_types DROP COLUMN color;
ALTER TABLE analysis_types DROP COLUMN bg_color;

-- 새로운 컬럼 추가
ALTER TABLE analysis_types ADD COLUMN thumb_image_url VARCHAR(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;

SELECT 'AnalysisType table updated successfully!' as message;
