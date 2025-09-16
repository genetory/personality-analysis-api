-- result_types 테이블의 label 컬럼을 title로 변경하는 마이그레이션 쿼리

-- 1. title 컬럼 추가 (label과 같은 타입으로)
ALTER TABLE result_types ADD COLUMN title VARCHAR(100);

-- 2. 기존 label 데이터를 title로 복사
UPDATE result_types SET title = label;

-- 3. title 컬럼을 NOT NULL로 설정
ALTER TABLE result_types ALTER COLUMN title SET NOT NULL;

-- 4. 기존 label 컬럼 삭제
ALTER TABLE result_types DROP COLUMN label;

-- 마이그레이션 완료 확인
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'result_types' 
ORDER BY ordinal_position;
