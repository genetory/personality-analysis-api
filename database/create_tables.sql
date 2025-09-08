-- 성향분석 데이터베이스 테이블 생성 스크립트
-- 데이터베이스: personality-analysis
-- 문자셋: utf8mb4_general_ci

USE `personality-analysis`;

-- 1. 사용자 테이블
CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL UNIQUE,
    `name` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `password_hash` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 2. 성향분석 유형 테이블
CREATE TABLE `analysis_types` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `description` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `category` VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `participants` INT DEFAULT 0,
    `color` VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `bg_color` VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `is_active` TINYINT(1) DEFAULT 1 COMMENT '0: 비활성, 1: 활성',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_category` (`category`),
    INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 3. 질문 테이블
CREATE TABLE `questions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `analysis_type_id` INT NOT NULL,
    `text` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `category` VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'empathy_vs_logic, active_vs_reflect, plan_vs_flow, express_vs_restrain',
    `axis` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '1, 2, 3, 4',
    `order_index` INT DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`analysis_type_id`) REFERENCES `analysis_types`(`id`) ON DELETE CASCADE,
    INDEX `idx_analysis_type` (`analysis_type_id`),
    INDEX `idx_category` (`category`),
    INDEX `idx_axis` (`axis`),
    INDEX `idx_order` (`order_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 4. 질문 선택지 테이블
CREATE TABLE `question_options` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `question_id` INT NOT NULL,
    `text` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `value` INT NOT NULL COMMENT '1-5 scale',
    `axis_score` FLOAT NOT NULL COMMENT '해당 축에 대한 점수 (-1.0 ~ 1.0)',
    `order_index` INT DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE CASCADE,
    INDEX `idx_question` (`question_id`),
    INDEX `idx_value` (`value`),
    INDEX `idx_order` (`order_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 5. 분석 결과 테이블
CREATE TABLE `analysis_results` (
    `id` VARCHAR(36) PRIMARY KEY COMMENT 'UUID',
    `user_id` INT NULL,
    `analysis_type_id` INT NOT NULL,
    `empathy_score` FLOAT NOT NULL COMMENT '에겐 vs 테토 (0-100)',
    `active_score` FLOAT NOT NULL COMMENT '액티브 vs 리플렉트 (0-100)',
    `plan_score` FLOAT NOT NULL COMMENT '플랜 vs 플로우 (0-100)',
    `express_score` FLOAT NOT NULL COMMENT '표현 vs 절제 (0-100)',
    `personality_type` VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `description` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `recommendations` JSON NULL COMMENT 'JSON 배열로 저장',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`analysis_type_id`) REFERENCES `analysis_types`(`id`) ON DELETE CASCADE,
    INDEX `idx_user` (`user_id`),
    INDEX `idx_analysis_type` (`analysis_type_id`),
    INDEX `idx_personality_type` (`personality_type`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 6. 답변 테이블
CREATE TABLE `answers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `analysis_result_id` VARCHAR(36) NOT NULL,
    `question_id` INT NOT NULL,
    `question_option_id` INT NOT NULL,
    `value` INT NOT NULL COMMENT '1-5 scale',
    FOREIGN KEY (`analysis_result_id`) REFERENCES `analysis_results`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`question_option_id`) REFERENCES `question_options`(`id`) ON DELETE CASCADE,
    INDEX `idx_result` (`analysis_result_id`),
    INDEX `idx_question` (`question_id`),
    INDEX `idx_option` (`question_option_id`),
    UNIQUE KEY `unique_result_question` (`analysis_result_id`, `question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 테이블 생성 완료 메시지
SELECT 'All tables created successfully!' as message;
