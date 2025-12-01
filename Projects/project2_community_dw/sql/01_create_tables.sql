-- =========================================
-- 1. Dimension Tables
-- =========================================

-- 1) 사용자 정보 테이블
CREATE TABLE IF NOT EXISTS dim_user (
    user_id      INTEGER PRIMARY KEY,           -- 사용자 고유 ID
    gender       TEXT,                          -- 성별 (M/F 등)
    age          INTEGER,                       -- 나이
    signup_date  DATE,                          -- 가입 일자
    region       TEXT                           -- 거주 지역
);

-- 2) 카테고리 정보 테이블
CREATE TABLE IF NOT EXISTS dim_category (
    category_id    INTEGER PRIMARY KEY,         -- 카테고리 고유 ID
    category_name  TEXT NOT NULL                -- 카테고리 이름 (예: Q&A, 자유게시판)
);

-- 3) 게시글 정보 테이블
CREATE TABLE IF NOT EXISTS dim_post (
    post_id      INTEGER PRIMARY KEY,           -- 게시글 고유 ID
    category_id  INTEGER NOT NULL,              -- 카테고리 ID (dim_category)
    author_id    INTEGER NOT NULL,              -- 작성자 사용자 ID (dim_user)
    created_at   DATETIME NOT NULL,             -- 게시글 작성 일시
    device_type  TEXT,                          -- 작성 기기 (PC, Mobile 등)

    FOREIGN KEY (category_id) REFERENCES dim_category (category_id),
    FOREIGN KEY (author_id)   REFERENCES dim_user (user_id)
);

-- =========================================
-- 2. Fact Table
-- =========================================

-- 4) 사용자 행동 로그 테이블
CREATE TABLE IF NOT EXISTS fact_user_action (
    action_id         INTEGER PRIMARY KEY,      -- 행동 고유 ID (로그 ID)
    user_id           INTEGER NOT NULL,         -- 사용자 ID (dim_user)
    post_id           INTEGER NOT NULL,         -- 게시글 ID (dim_post)
    action_type       TEXT NOT NULL,            -- 행동 종류 (view, like, comment 등)
    action_timestamp  DATETIME NOT NULL,        -- 행동 발생 일시
    session_id        TEXT,                     -- 세션 ID

    FOREIGN KEY (user_id) REFERENCES dim_user (user_id),
    FOREIGN KEY (post_id) REFERENCES dim_post (post_id)
);

-- =========================================
-- 3. Index 설정 (조회 성능 향상용)
-- =========================================

-- 사용자별 행동 조회를 빠르게 하기 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_fact_user_action_user
    ON fact_user_action (user_id);

-- 게시글별 행동 조회를 빠르게 하기 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_fact_user_action_post
    ON fact_user_action (post_id);

-- 날짜 기준 통계(DAU/WAU/MAU 등)를 위해 타임스탬프 인덱스
CREATE INDEX IF NOT EXISTS idx_fact_user_action_ts
    ON fact_user_action (action_timestamp);
