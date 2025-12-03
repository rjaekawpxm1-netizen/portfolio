🧾 주문 데이터 자동 수집 & 리포트 생성 RPA 파이프라인

웹 주문 데이터를 자동으로 크롤링하여 CSV로 저장하고,
일일 매출 리포트를 자동 생성한 뒤 Slack으로 알림을 보내는 엔드투엔드 RPA 자동화 시스템입니다.

반복되는 운영 업무를 자동화하는 것을 목표로 설계했습니다.

📁 프로젝트 구조
project3_rpa_order_pipeline/
│
├── rpa_order_pipeline/
│   ├── __init__.py
│   ├── config.py                 # 환경변수 및 경로 설정
│   ├── main.py                   # 전체 파이프라인 실행
│   │
│   ├── crawler/
│   │   ├── __init__.py
│   │   └── fetch_orders.py       # 주문 데이터 크롤링 (Selenium)
│   │
│   ├── processor/
│       ├── __init__.py
│       └── build_report.py       # 리포트 생성 (Pandas + Excel)
│
└── notifier/
    ├── __init__.py
    └── slack_notify.py           # Slack Webhook 알림
│
├── data/
│   ├── raw/                      # 주문 원본 데이터 (CSV)
│   └── reports/                  # 자동 생성된 Excel 리포트
│
├── img/                          # README 이미지 저장용
├── requirements.txt              # 설치 패키지 목록
└── README.md

🎯 프로젝트 목표

매일 반복되는 주문 현황 취합 업무 자동화

웹페이지 → CSV → Excel 리포트 → Slack 알림까지 완전 자동 파이프라인 구축

데이터 수집, 전처리, 리포트 자동화 경험 어필

실제 운영 환경에서도 적용 가능한 구조로 설계

🚀 기능 요약
✔ 1. 웹 주문 데이터 자동 크롤링

Selenium & WebDriverManager 사용

headless 모드로 브라우저 없이 실행 가능

테이블 데이터를 자동 추출

data/raw/orders.csv 저장

※ 실제 사이트를 연결하지 않은 경우, 기본 구조만 생성되고 내용은 비어 있음

✔ 2. 더미 데이터 자동 생성(Fallback)

크롤링된 데이터가 없거나 CSV가 비어있으면:

자동으로 더미 주문 데이터를 생성

파이프라인이 중단되지 않고 계속 진행됨

📌 자동화 시스템의 안정성을 위한 핵심 기능

✔ 3. Excel 매출 리포트 자동 생성

리포트 내용:

총 주문 수

총 판매 수량

총 매출

제품별 판매량 및 매출 정렬

서식 포함된 Excel 파일 생성

저장 경로:

data/reports/report.xlsx

✔ 4. Slack 자동 알림

리포트 생성이 완료되면 Slack Webhook으로 메시지 전송

.env 파일에서 Webhook URL 설정

URL이 없으면 자동으로 Slack 단계 skip

⚙️ 설치 & 실행 방법
1️⃣ 패키지 설치
pip install -r requirements.txt

2️⃣ .env 파일 생성

프로젝트 루트에 .env 생성 후:

ORDER_URL=https://example.com/orders
SLACK_WEBHOOK_URL=


(실제 URL & Slack Webhook 넣으면 바로 실서비스로 전환 가능)

3️⃣ 파이프라인 실행

프로젝트 루트에서:

python -m rpa_order_pipeline.main

🖥 실행 예시 로그
=== [1/3] 주문 데이터 크롤링 ===
[INFO] 웹 주문 데이터 크롤링 시작...
[INFO] 크롤링 완료 → data/raw/orders.csv

=== [2/3] 리포트 생성 ===
[INFO] 주문 데이터 불러오는 중...
[WARN] 주문 데이터가 없어 더미 데이터를 생성합니다.
[INFO] 리포트 생성 완료 → data/reports/report.xlsx

=== [3/3] Slack 알림 전송 ===
[WARN] SLACK_WEBHOOK_URL 이 설정되지 않아 슬랙 알림을 건너뜁니다.

=== 파이프라인 완료 ===

🧠 기술적 특징
🔹 Selenium + WebDriverManager

크롬드라이버 버전 호환 문제를 자동 해결

추가 설치 없이 자동 다운로드

🔹 Pandas 기반 데이터 전처리

수량/가격 numeric 변환

매출(amount) 계산

GroupBy 집계

🔹 Excel 자동화(openpyxl)

Summary Sheet / Product Summary Sheet

제목 굵기 & 스타일 적용

🔹 Slack Webhook 연동

CI 환경에서도 사용 가능

운영 자동화 작업에 즉시 도입 가능

📌 향후 확장 아이디어

PowerPoint 자동 생성 (python-pptx)

특정 주문 이상치 Slack 알림

자동 이메일 발송 기능 추가

Airflow를 통한 스케줄링

쿠팡/네이버 스마트스토어 API 자동 연동

✔ 프로젝트 한 줄 요약

반복 업무를 완전 자동화한 RPA 파이프라인 구현 경험을 보여주는 프로젝트.
데이터 수집 → 정제 → 리포트 생성 → 알림까지 이어지는 실전 자동화 흐름을 담고 있음.