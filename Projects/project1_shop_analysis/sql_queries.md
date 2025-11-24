# 🧾 SQL Queries 모음 (온라인 쇼핑몰 분석)

이 문서는 `shop.db`(SQLite)에서 사용한 **주요 SQL 쿼리**를 정리한 것이다.  
데이터 생성용 DDL과 분석용 쿼리로 나누어 정리하였다.

---

## 1. 테이블 생성 (DDL)

```sql
CREATE TABLE IF NOT EXISTS customers (
    customer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    gender        TEXT,
    age           INTEGER,
    join_date     DATE,
    region        TEXT
);

CREATE TABLE IF NOT EXISTS products (
    product_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name  TEXT,
    category      TEXT,
    price         INTEGER,
    created_at    DATE
);

CREATE TABLE IF NOT EXISTS orders (
    order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id   INTEGER,
    order_date    DATETIME,
    order_status  TEXT,
    payment_method TEXT,
    device_type   TEXT
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id      INTEGER,
    product_id    INTEGER,
    quantity      INTEGER,
    unit_price    INTEGER
);
```

---

## 2. 초기화 쿼리 (데이터 전체 삭제)

```sql
DELETE FROM order_items;
DELETE FROM orders;
DELETE FROM products;
DELETE FROM customers;
```

---

## 3. 분석 쿼리

### 3-1. 월별 매출 & 주문 수

```sql
SELECT
    strftime('%Y-%m', o.order_date) AS ym,
    SUM(oi.quantity * oi.unit_price) AS revenue,
    COUNT(DISTINCT o.order_id) AS num_orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'paid'
GROUP BY ym
ORDER BY ym;
```

---

### 3-2. 카테고리별 매출

```sql
SELECT
    p.category,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'paid'
GROUP BY p.category
ORDER BY revenue DESC;
```

---

### 3-3. 성별 · 연령대별 평균 주문금액(AOV) & 주문 수

```sql
WITH order_amounts AS (
    SELECT
        o.order_id,
        o.customer_id,
        SUM(oi.quantity * oi.unit_price) AS amount
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'paid'
    GROUP BY o.order_id
)
SELECT
    c.gender,
    CASE
        WHEN c.age < 20 THEN '10대 이하'
        WHEN c.age BETWEEN 20 AND 29 THEN '20대'
        WHEN c.age BETWEEN 30 AND 39 THEN '30대'
        WHEN c.age BETWEEN 40 AND 49 THEN '40대'
        ELSE '50대 이상'
    END AS age_group,
    COUNT(*) AS num_orders,
    AVG(amount) AS avg_order_value
FROM order_amounts oa
JOIN customers c ON oa.customer_id = c.customer_id
GROUP BY c.gender, age_group
ORDER BY age_group, c.gender;
```

---

### 3-4. 고객별 주문 횟수 & 재구매율 분석용 기초 쿼리

```sql
SELECT
    customer_id,
    COUNT(DISTINCT order_id) AS order_count
FROM orders
WHERE order_status = 'paid'
GROUP BY customer_id;
```

---

### 3-5. 디바이스 · 결제수단별 매출

```sql
SELECT
    o.device_type,
    o.payment_method,
    COUNT(DISTINCT o.order_id) AS num_orders,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'paid'
GROUP BY o.device_type, o.payment_method
ORDER BY revenue DESC;
```

---

### 3-6. (선택) 요일별 매출 분석 예시 쿼리

```sql
SELECT
    strftime('%w', o.order_date) AS weekday,
    SUM(oi.quantity * oi.unit_price) AS revenue,
    COUNT(DISTINCT o.order_id) AS num_orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'paid'
GROUP BY weekday
ORDER BY weekday;
```

---

## 4. 요약

- 위 쿼리들은 `shop_analysis_clean.ipynb`에서 사용된 핵심 SQL 쿼리이다.  
- 데이터 집계는 **SQL에서 최대한 수행**하고,  
  후처리와 시각화는 **pandas + matplotlib**로 처리하였다.
