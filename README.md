📁 Data Analysis Portfolio

다양한 SQL·Python·대시보드 기반 데이터 분석 프로젝트를 정리한 포트폴리오입니다.
(모든 프로젝트는 /Projects 폴더에서 확인할 수 있습니다.)

📁 1. SQL 프로젝트

SQL 문법 학습부터 실제 분석 환경에서 활용 가능한 중급 분석까지 구성되어 있습니다.

📝 SQL 기초 문법 학습

📊 Group By / Join / Window Function 실습

📈 쇼핑몰 더미 데이터를 활용한 분석 실전 문제

👉 상세 내용: /SQL 폴더 참고

📁 2. Python 코딩

데이터 전처리부터 시각화, 간단한 모델링까지 실제 분석 흐름을 실습한 코드들입니다.

pandas 를 활용한 데이터 전처리

EDA(탐색적 데이터 분석)

기본 머신러닝 모델 적용

matplotlib/seaborn 기반 시각화

👉 상세 내용: /Python 폴더 참고

📁 3. Projects

작은 실습형 프로젝트부터 실제 분석 흐름을 구현한 프로젝트까지 정리했습니다.

🛒 01. 온라인 쇼핑몰 데이터 분석 (SQL + Python)

랜덤 더미 데이터를 생성하고, SQLite 기반 쇼핑몰 DB를 구현한 뒤
고객·매출·재구매 지표를 분석한 프로젝트입니다.

✔ 요약

더미 고객/상품/주문 데이터를 생성해 DB 구축

SQL로 매출·고객 행동 분석

Python으로 AOV, 재구매 패턴 시각화

✔ 사용 기술

Python, SQLite, pandas, matplotlib

✔ 핵심 성과

월별, 카테고리별, 디바이스/결제수단 매출 분석

성별·연령대별 AOV 시각화

재구매 고객 행동 분석

📂 파일 위치: Projects/01_ShoppingMall_Analysis
👉 자세히 보기: /Projects/01_ShoppingMall_Analysis

🔮 02. 고객 이탈 예측 모델링 (Churn Prediction)

프로젝트 1에서 만든 쇼핑몰 DB를 기반으로
1회 구매 고객의 "이탈 여부"를 머신러닝으로 예측하는 모델을 구축했습니다.

✔ 요약

고객별 구매 패턴 기반 Feature Engineering 수행

Logistic Regression / RandomForest 비교

Feature Importance 분석으로 행동 패턴 도출

✔ 사용 기술

Python, pandas, SQLite, Scikit-Learn, matplotlib

✔ 핵심 성과

Accuracy = 1.00, F1-score = 1.00

중요 Feature: Total Orders, Days Between 등

전처리 중 "평균치가 너무 작아 시각화가 안 보이는 문제" 해결
→ 데이터 dtype 재확인 및 scaling 방식 조정 후 해결

📂 파일 위치: Projects/02_Churn_Prediction
👉 자세히 보기: /Projects/02_Churn_Prediction

📊 03. 고객 구매 행동 대시보드 (Tableau + Power BI)

프로젝트 1·2에서 만든 데이터를 기반으로,
Tableau와 Power BI에서 고객 구매·이탈·세그먼트 분석 대시보드를 구축했습니다.

🟦 사용 도구

Tableau Desktop

Power BI Desktop

CSV / SQLite 데이터 연결

고객 행동지표(KPI) 설계

🟧 Tableau 주요 구성 요소
1) 고객 이탈/유지 비율 분석

COUNT(Customer ID) 기반 Pie Chart

Churn Label로 색상 구분

평균값이 매우 작아 그래프가 보이지 않는 문제 → 전처리 수정 + 시각화 방식 변경으로 해결

2) 구매 간격(Days Between) 분석

주문 간 Days Between 막대 비교

분포 히스토그램 생성

값이 0으로 몰리는 문제 → Scaling / Bin 조정으로 해결

3) 고객 세그먼트 분석

고가치 / 저가치 고객 분류

구매 금액, 빈도, 재구매 간격 기반 KPI 구성

🟨 Power BI 주요 구성 요소
1) 이탈/유지 KPI 카드

총 고객 수

Churn=1 비율

유지 고객 비율

2) 고객 행동 분석

주문 횟수/총 금액 기반 KPI

성별/연령/디바이스별 패턴 분리(Slicer)

3) 구매주기 히스토그램

Days Between의 분포 시각화

누적 필터링을 통한 드릴다운 기능 구현

📂 파일 위치: Projects/03_Dashboard
👉 자세히 보기: /Projects/03_Dashboard

📧 Contact

Email: your-email@example.com

GitHub: https://github.com/your-github

Notion/Blog (선택): link_here

⭐ 앞으로 지속적으로 업데이트할 예정입니다.