-- =========================================
-- 1. DAU / WAU / MAU
-- =========================================

-- Daily Active Users (DAU)
SELECT 
    DATE(action_timestamp) AS action_date,
    COUNT(DISTINCT user_id) AS dau
FROM fact_user_action
GROUP BY DATE(action_timestamp)
ORDER BY action_date;

-- Weekly Active Users (WAU)
SELECT 
    STRFTIME('%Y-%W', action_timestamp) AS year_week,
    COUNT(DISTINCT user_id) AS wau
FROM fact_user_action
GROUP BY STRFTIME('%Y-%W', action_timestamp)
ORDER BY year_week;

-- Monthly Active Users (MAU)
SELECT
    STRFTIME('%Y-%m', action_timestamp) AS year_month,
    COUNT(DISTINCT user_id) AS mau
FROM fact_user_action
GROUP BY STRFTIME('%Y-%m', action_timestamp)
ORDER BY year_month;

-- =========================================
-- 2. Retention 분석 (D0, D1, D7)
-- =========================================

WITH first_visit AS (
    SELECT 
        user_id,
        MIN(DATE(action_timestamp)) AS first_date
    FROM fact_user_action
    GROUP BY user_id
),
daily_active AS (
    SELECT 
        user_id,
        DATE(action_timestamp) AS active_date
    FROM fact_user_action
)
SELECT
    f.first_date,
    COUNT(CASE WHEN d.active_date = f.first_date THEN 1 END) AS day0_users,
    COUNT(CASE WHEN d.active_date = f.first_date + 1 THEN 1 END) AS d1_users,
    COUNT(CASE WHEN d.active_date = f.first_date + 7 THEN 1 END) AS d7_users
FROM first_visit f
LEFT JOIN daily_active d
    ON f.user_id = d.user_id
GROUP BY f.first_date
ORDER BY f.first_date;

-- =========================================
-- 3. 카테고리별 조회→좋아요 전환율
-- =========================================

SELECT
    c.category_name,
    COUNT(CASE WHEN a.action_type = 'view' THEN 1 END) AS views,
    COUNT(CASE WHEN a.action_type = 'like' THEN 1 END) AS likes,
    ROUND(
        CAST(COUNT(CASE WHEN a.action_type = 'like' THEN 1 END) AS REAL)
        / NULLIF(COUNT(CASE WHEN a.action_type = 'view' THEN 1 END), 0),
        3
    ) AS view_to_like_rate
FROM fact_user_action a
JOIN dim_post p
    ON a.post_id = p.post_id
JOIN dim_category c
    ON p.category_id = c.category_id
GROUP BY c.category_name
ORDER BY views DESC;

-- =========================================
-- 4. 사용자 상태 분류 (Active / Dormant / Churn)
-- =========================================

SELECT
    u.user_id,
    u.gender,
    u.age,
    MAX(DATE(a.action_timestamp)) AS last_active_date,
    CASE
        WHEN MAX(DATE(a.action_timestamp)) >= DATE('now', '-7 day') THEN 'Active'
        WHEN MAX(DATE(a.action_timestamp)) >= DATE('now', '-30 day') THEN 'Dormant'
        ELSE 'Churn'
    END AS user_status
FROM dim_user u
LEFT JOIN fact_user_action a
    ON u.user_id = a.user_id
GROUP BY u.user_id, u.gender, u.age
ORDER BY last_active_date DESC;
