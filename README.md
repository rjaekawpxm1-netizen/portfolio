## 📁 1. SQL Projects
> SQL 문법 학습 + 중급 분석 쿼리 실습

- 📝 SQL 기초 문제 풀이  
- 📊 Group By / Join / Window Function  
- 📈 데이터 분석용 SQL 실전 문제  

👉 상세 내용: **`/SQL` 폴더 참고**

---

## 📁 2. Python Coding
> 데이터 전처리, 시각화, 모델링 중심 학습 코드

- `pandas` 데이터 전처리 실습  
- EDA(탐색적 데이터 분석)  
- 기본 머신러닝 모델 실습  
- matplotlib/seaborn 시각화  

👉 상세 내용: **`/Python` 폴더 참고**

---

## 📁 3. Projects
> 작은 프로젝트부터 실전 데이터 분석 프로젝트까지 정리

---

### 🛒 01. 온라인 쇼핑몰 데이터 분석 (SQL + Python)
- **요약:** 랜덤 더미 데이터 생성 → SQLite DB 구축 → 매출/고객/재구매 분석  
- **사용 기술:** Python, SQLite, pandas, matplotlib  
- **핵심 성과:**  
  - 월별 매출, 카테고리 매출, 디바이스/결제수단 매출 분석  
  - 성별·연령대별 AOV 분석  
  - 재구매 고객군 행동 분석  
- **파일 위치:** `Projects/01_ShoppingMall_Analysis`

👉 자세한 내용: `/Projects/01_ShoppingMall_Analysis`

---

### 🔮 02. 고객 이탈 예측 모델링 (Churn Prediction)
- **요약:** Project1에서 생성된 쇼핑몰 데이터를 기반으로  
  고객의 *이탈 가능성(1회 구매 고객)* 을 머신러닝으로 예측  
- **사용 기술:** Python, pandas, SQLite, Scikit-Learn, matplotlib  
- **핵심 성과:**  
  - 고객별 구매 패턴 분석(주문 횟수, 평균 간격 등 Feature Engineering)  
  - Logistic Regression / RandomForest 모델 적용  
  - **Accuracy = 1.00 / F1-score = 1.00**  
  - Feature Importance 분석을 통해 행동 패턴 인사이트 도출  
- **파일 위치:** `Projects/02_Churn_Prediction`
- **시각화 예시:**  
  - Feature Importance  
  - Confusion Matrix  

👉 자세한 내용: `/Projects/02_Churn_Prediction`

---

📊 03. 고객 구매 행동 대시보드 (Tableau + Power BI)

Project 1 & 2의 데이터를 시각화 도구(Tableau / Power BI)에서 활용하여
고객 구매 패턴·이탈·세그먼트 분석 대시보드를 구축한 프로젝트입니다.

📌 사용 기술

Tableau Desktop

Power BI Desktop

CSV / SQLite 데이터 연결

KPI 지표 설계

📌 Tableau 시각화 구성 요소
1) 고객 이탈/유지 비율 파이차트

COUNT(Customer ID)를 통해 비율 계산

Churn Label로 색상 구분

평균값이 너무 작아 값이 보이지 않는 문제를
→ 데이터 전처리 개선 + 레이블 표시 방식 변경 으로 해결

2) Total Orders / Days Between 분석

주문 횟수별 고객 분포

구매 간격(Days Between) 히스토그램

구매 횟수별 이탈 고객 비율 비교

3) 고객 세그먼트 분석

High-value / Low-value 고객 분류

구매 주기, 재구매 패턴, LTV 기반

Segment별 KPI 추출

📌 Power BI 시각화 구성 요소
1) 고객 이탈 분석 보고서

Churn Label을 기준으로 KPI 카드 구성

세그먼트별 이탈 비율 바 차트

파이 차트로 유지/이탈 비율 표현

2) 구매 간격 분석(히스토그램)

Days Between 분포

구매 빈도별 고객 생애 가치(LTV) 시각화

필터 슬라이서로 연령/성별/디바이스별 분리 분석

3) 매출 및 고객 행동 분석

Total Orders / Total Amount 기준 KPI

Customer ID 기반 Drill-Down 기능

다양한 시각 요소를 통한 인사이트 탐색

파일 위치:


👉 자세한 내용: /Projects/03_dashboard

## 📧 Contact
- Email: your-email@example.com  
- GitHub: https://github.com/your-github  
- Notion/Blog (선택): link_here  

---

### ⭐ 앞으로 지속적으로 업데이트할 예정입니다.
