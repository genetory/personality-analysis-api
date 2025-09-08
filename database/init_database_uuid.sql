-- UUID 기반 데이터베이스 전체 초기화 스크립트

-- 기존 테이블 삭제 (외래키 제약조건 때문에 순서 중요)
DROP TABLE IF EXISTS answers;
DROP TABLE IF EXISTS analysis_results;
DROP TABLE IF EXISTS question_options;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS analysis_types;
DROP TABLE IF EXISTS users;

-- 사용자 테이블
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    email VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci UNIQUE NOT NULL,
    name VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    password_hash VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 성향분석 유형 테이블
CREATE TABLE analysis_types (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    description TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    category VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    participants INT DEFAULT 0,
    color VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    bg_color VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    is_active INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 질문 테이블
CREATE TABLE questions (
    id CHAR(36) PRIMARY KEY,
    analysis_type_id CHAR(36) NOT NULL,
    text TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    category VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    axis VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    order_index INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_type_id) REFERENCES analysis_types(id) ON DELETE CASCADE,
    INDEX idx_analysis_type (analysis_type_id),
    INDEX idx_category (category),
    INDEX idx_axis (axis)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 질문 선택지 테이블
CREATE TABLE question_options (
    id CHAR(36) PRIMARY KEY,
    question_id CHAR(36) NOT NULL,
    text TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    value INT NOT NULL,
    axis_score FLOAT NOT NULL,
    order_index INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    INDEX idx_question (question_id),
    INDEX idx_value (value)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 분석 결과 테이블
CREATE TABLE analysis_results (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NULL,
    analysis_type_id CHAR(36) NOT NULL,
    empathy_score FLOAT NOT NULL,
    active_score FLOAT NOT NULL,
    plan_score FLOAT NOT NULL,
    express_score FLOAT NOT NULL,
    personality_type VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    description TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    recommendations JSON NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (analysis_type_id) REFERENCES analysis_types(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_analysis_type (analysis_type_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 답변 테이블
CREATE TABLE answers (
    id CHAR(36) PRIMARY KEY,
    analysis_result_id CHAR(36) NOT NULL,
    question_id CHAR(36) NOT NULL,
    question_option_id CHAR(36) NOT NULL,
    value INT NOT NULL,
    FOREIGN KEY (analysis_result_id) REFERENCES analysis_results(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (question_option_id) REFERENCES question_options(id) ON DELETE CASCADE,
    INDEX idx_analysis_result (analysis_result_id),
    INDEX idx_question (question_id),
    INDEX idx_question_option (question_option_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 성향분석 유형 삽입
INSERT INTO analysis_types (id, name, description, category, participants, color, bg_color, is_active) VALUES
('550e8400-e29b-41d4-a716-446655440001', '4축 성향분석', '에겐/테토, 액티브/리플렉트, 플랜/플로우, 표현/절제로 나를 완전히 이해하는 분석', '성격', 1250000, 'text-blue-600', 'bg-blue-50', 1);

-- 질문 삽입 (1축: 에겐 vs 테토)
INSERT INTO questions (id, analysis_type_id, text, category, axis, order_index) VALUES
('550e8400-e29b-41d4-a716-446655440101', '550e8400-e29b-41d4-a716-446655440001', '친구가 "멘탈 터졌다"라고 톡 보냈을 때', 'empathy_vs_logic', '1', 1),
('550e8400-e29b-41d4-a716-446655440102', '550e8400-e29b-41d4-a716-446655440001', '새로운 모임에 갔을 때 내 모습은?', 'empathy_vs_logic', '1', 2),
('550e8400-e29b-41d4-a716-446655440103', '550e8400-e29b-41d4-a716-446655440001', '중요한 선택의 순간!', 'empathy_vs_logic', '1', 3),
('550e8400-e29b-41d4-a716-446655440104', '550e8400-e29b-41d4-a716-446655440001', '친구랑 다퉜을 때', 'empathy_vs_logic', '1', 4);

-- 질문 삽입 (2축: 액티브 vs 리플렉트)
INSERT INTO questions (id, analysis_type_id, text, category, axis, order_index) VALUES
('550e8400-e29b-41d4-a716-446655440201', '550e8400-e29b-41d4-a716-446655440001', '주말에 더 끌리는 건?', 'active_vs_reflect', '2', 5),
('550e8400-e29b-41d4-a716-446655440202', '550e8400-e29b-41d4-a716-446655440001', '새로운 카페에 갔을 때', 'active_vs_reflect', '2', 6),
('550e8400-e29b-41d4-a716-446655440203', '550e8400-e29b-41d4-a716-446655440001', '모임에서 나는…', 'active_vs_reflect', '2', 7),
('550e8400-e29b-41d4-a716-446655440204', '550e8400-e29b-41d4-a716-446655440001', '여행 중 갑자기 문제가 생겼다!', 'active_vs_reflect', '2', 8);

-- 질문 삽입 (3축: 플랜 vs 플로우)
INSERT INTO questions (id, analysis_type_id, text, category, axis, order_index) VALUES
('550e8400-e29b-41d4-a716-446655440301', '550e8400-e29b-41d4-a716-446655440001', '여행 준비할 때 나는?', 'plan_vs_flow', '3', 9),
('550e8400-e29b-41d4-a716-446655440302', '550e8400-e29b-41d4-a716-446655440001', '프로젝트 맡으면', 'plan_vs_flow', '3', 10),
('550e8400-e29b-41d4-a716-446655440303', '550e8400-e29b-41d4-a716-446655440001', '평소 생활 패턴', 'plan_vs_flow', '3', 11),
('550e8400-e29b-41d4-a716-446655440304', '550e8400-e29b-41d4-a716-446655440001', '약속 있을 때 나는?', 'plan_vs_flow', '3', 12);

-- 질문 삽입 (4축: 표현 vs 절제)
INSERT INTO questions (id, analysis_type_id, text, category, axis, order_index) VALUES
('550e8400-e29b-41d4-a716-446655440401', '550e8400-e29b-41d4-a716-446655440001', '좋은 일 생겼을 때', 'express_vs_restrain', '4', 13),
('550e8400-e29b-41d4-a716-446655440402', '550e8400-e29b-41d4-a716-446655440001', '말할 때 스타일은?', 'express_vs_restrain', '4', 14),
('550e8400-e29b-41d4-a716-446655440403', '550e8400-e29b-41d4-a716-446655440001', '내가 실수했을 때', 'express_vs_restrain', '4', 15),
('550e8400-e29b-41d4-a716-446655440404', '550e8400-e29b-41d4-a716-446655440001', '칭찬 받을 때', 'express_vs_restrain', '4', 16);

-- 질문 선택지 삽입 (1축: 에겐 vs 테토)
INSERT INTO question_options (id, question_id, text, value, axis_score, order_index) VALUES
-- 질문 1
('550e8400-e29b-41d4-a716-446655441101', '550e8400-e29b-41d4-a716-446655440101', 'A: "야 ㅠㅠ 힘들었겠다" → 바로 공감', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655441102', '550e8400-e29b-41d4-a716-446655440101', 'B: "무슨 상황이야?" → 상황부터 분석', 2, -1.0, 2),
-- 질문 2
('550e8400-e29b-41d4-a716-446655441201', '550e8400-e29b-41d4-a716-446655440102', 'A: 눈 마주치면 바로 "안녕하세요~✌️"', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655441202', '550e8400-e29b-41d4-a716-446655440102', 'B: 조용히 분위기 먼저 스캔👀', 2, -1.0, 2),
-- 질문 3
('550e8400-e29b-41d4-a716-446655441301', '550e8400-e29b-41d4-a716-446655440103', 'A: 그냥 내 촉 믿고 간다 (느낌 가는 대로)', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655441302', '550e8400-e29b-41d4-a716-446655440103', 'B: 근거·정보 모으고 정리부터', 2, -1.0, 2),
-- 질문 4
('550e8400-e29b-41d4-a716-446655441401', '550e8400-e29b-41d4-a716-446655440104', 'A: "미안해ㅠㅠ 우리 다시 잘 지내자" → 감정 회복 먼저', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655441402', '550e8400-e29b-41d4-a716-446655440104', 'B: "왜 그랬는지 정리해보자" → 원인 파악부터', 2, -1.0, 2);

-- 질문 선택지 삽입 (2축: 액티브 vs 리플렉트)
INSERT INTO question_options (id, question_id, text, value, axis_score, order_index) VALUES
-- 질문 5
('550e8400-e29b-41d4-a716-446655442101', '550e8400-e29b-41d4-a716-446655440201', 'A: 약속 꽉꽉 채워 놀러 다니기 🏃', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655442102', '550e8400-e29b-41d4-a716-446655440201', 'B: 집콕하면서 혼자 충전하기 😌', 2, -1.0, 2),
-- 질문 6
('550e8400-e29b-41d4-a716-446655442201', '550e8400-e29b-41d4-a716-446655440202', 'A: "와 여기 인테리어 대박" → 바로 인증샷📸', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655442202', '550e8400-e29b-41d4-a716-446655440202', 'B: 자리 앉고 조용히 분위기부터 탐색', 2, -1.0, 2),
-- 질문 7
('550e8400-e29b-41d4-a716-446655442301', '550e8400-e29b-41d4-a716-446655440203', 'A: 분위기 띄우는 핵인싸 🎤', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655442302', '550e8400-e29b-41d4-a716-446655440203', 'B: 듣다가 필요할 때만 톡 쏘는 한마디 🎯', 2, -1.0, 2),
-- 질문 8
('550e8400-e29b-41d4-a716-446655442401', '550e8400-e29b-41d4-a716-446655440204', 'A: "일단 가자!" → 몸 먼저 움직임', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655442402', '550e8400-e29b-41d4-a716-446655440204', 'B: "잠깐만… 옵션 뭐 있어?" → 머리부터 굴림', 2, -1.0, 2);

-- 질문 선택지 삽입 (3축: 플랜 vs 플로우)
INSERT INTO question_options (id, question_id, text, value, axis_score, order_index) VALUES
-- 질문 9
('550e8400-e29b-41d4-a716-446655443101', '550e8400-e29b-41d4-a716-446655440301', 'A: 숙소/교통/일정 싹 다 정리 ✅', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655443102', '550e8400-e29b-41d4-a716-446655440301', 'B: 그냥 가서 되는 대로 놀자 🌊', 2, -1.0, 2),
-- 질문 10
('550e8400-e29b-41d4-a716-446655443201', '550e8400-e29b-41d4-a716-446655440302', 'A: 역할·타임라인 정리해서 진행', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655443202', '550e8400-e29b-41d4-a716-446655440302', 'B: 상황 보고 그때그때 유연하게', 2, -1.0, 2),
-- 질문 11
('550e8400-e29b-41d4-a716-446655443301', '550e8400-e29b-41d4-a716-446655440303', 'A: 루틴 좋아함, 스케줄 지키는 편', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655443302', '550e8400-e29b-41d4-a716-446655440303', 'B: 오늘 기분 따라 움직이는 편', 2, -1.0, 2),
-- 질문 12
('550e8400-e29b-41d4-a716-446655443401', '550e8400-e29b-41d4-a716-446655440304', 'A: 10분 일찍 도착해서 대기 ⏰', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655443402', '550e8400-e29b-41d4-a716-446655440304', 'B: "조금 늦어도 뭐~" 여유롭게 🛋️', 2, -1.0, 2);

-- 질문 선택지 삽입 (4축: 표현 vs 절제)
INSERT INTO question_options (id, question_id, text, value, axis_score, order_index) VALUES
-- 질문 13
('550e8400-e29b-41d4-a716-446655444101', '550e8400-e29b-41d4-a716-446655440401', 'A: 단톡에 바로 공유 + 이모티콘 난사 🥳', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655444102', '550e8400-e29b-41d4-a716-446655440401', 'B: 속으로 뿌듯, 티는 잘 안 냄 🙂', 2, -1.0, 2),
-- 질문 14
('550e8400-e29b-41d4-a716-446655444201', '550e8400-e29b-41d4-a716-446655440402', 'A: 하고 싶은 말 직설적으로 팍팍', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655444202', '550e8400-e29b-41d4-a716-446655440402', 'B: 상대 기분 고려해서 돌려서', 2, -1.0, 2),
-- 질문 15
('550e8400-e29b-41d4-a716-446655444301', '550e8400-e29b-41d4-a716-446655440403', 'A: 바로 "아 미안해 ㅠㅠ" 하고 감정 드러냄', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655444302', '550e8400-e29b-41d4-a716-446655440403', 'B: 조용히 행동으로 만회', 2, -1.0, 2),
-- 질문 16
('550e8400-e29b-41d4-a716-446655444401', '550e8400-e29b-41d4-a716-446655440404', 'A: "오 진짜? 고마워!" → 바로 리액션', 1, 1.0, 1),
('550e8400-e29b-41d4-a716-446655444402', '550e8400-e29b-41d4-a716-446655440404', 'B: 겉으론 무심, 속으론 뿌듯ㅎㅎ', 2, -1.0, 2);

SELECT 'Database initialized successfully with UUID!' as message;
