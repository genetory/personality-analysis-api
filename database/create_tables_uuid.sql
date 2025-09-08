-- UUID 기반 테이블 생성 스크립트
-- 모든 ID 필드를 CHAR(36) UUID로 변경

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

SELECT 'All tables created successfully with UUID!' as message;
