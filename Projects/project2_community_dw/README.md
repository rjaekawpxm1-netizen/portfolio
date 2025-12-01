🛒 커뮤니티 사용자 행동 분석 대시보드 (DAU · WAU · MAU)

본 프로젝트는 커뮤니티 서비스 사용자 행동 데이터를 기반으로 운영 지표(DAU, WAU, MAU)를 분석하고
Tableau로 시각화한 인터랙티브 대시보드를 구축한 프로젝트입니다.

데이터는 실제 서비스를 가정하여 CSV 형태의 더미 데이터를 생성하고,
이를 Python으로 통합하여 Datamart 형태의 community_dw_full.csv 파일을 제작했습니다.

📘 프로젝트 개요
항목	내용
목적	사용자 활성 지표 분석(DAU·WAU·MAU) 및 대시보드 구축
기술 스택	Python(pandas), Tableau, ERD(dbdiagram.io), GitHub
주요 산출물	통합 데이터셋, ERD, Tableau 대시보드, KPI 텍스트 KPI 카드
📂 폴더 구조
project2_community_dw/
│
├── data_raw/              # 원본 더미데이터
│   ├── users.csv
│   ├── posts.csv
│   ├── categories.csv
│   └── actions.csv
│
├── data_processed/
│   └── community_dw_full.csv
│
├── img/
│   └── erd.png            # ERD 이미지
│
├── tableau/
│   └── dashboard.twbx     # Tableau 대시보드 파일
│
└── README.md

📊 ERD (Entity Relationship Diagram)

본 프로젝트는 사용자 행동 분석을 위해 아래와 같은 4개 테이블로 구성된 Schema를 사용했습니다.

users — 사용자 기본 정보

posts — 게시글 정보

categories — 게시글 카테고리 정보

actions — 사용자 행동 로그(조회, 좋아요, 댓글 등)

✔ 테이블 구조 관계
관계	설명
users 1 ── N posts	유저는 여러 게시글을 작성할 수 있음
categories 1 ── N posts	한 카테고리에 여러 게시글 포함
users 1 ── N actions	유저는 여러 행동을 할 수 있음
posts 1 ── N actions	게시물에도 여러 행동이 발생 가능
✔ ERD 이미지
![ERD](./img/erd.png)

🧩 데이터 통합 과정 (Python)

원본 4개 CSV(users, posts, categories, actions)를
아래 Python 코드로 하나의 Fact Table로 병합했습니다.

🔧 Python 전처리 코드
import pandas as pd

users = pd.read_csv("users.csv")
posts = pd.read_csv("posts.csv")
categories = pd.read_csv("categories.csv")
actions = pd.read_csv("actions.csv")

# posts에 카테고리 정보 merge
posts_full = posts.merge(categories, on="category_id", how="left")

# actions 중심으로 완전한 사용자 행동 데이터셋 생성
full = (
    actions
    .merge(users, on="user_id", how="left")
    .merge(posts_full, on="post_id", how="left")
)

# 저장
full.to_csv("community_dw_full.csv", index=False)


📌 최종 결과:
→ Tableau로 바로 분석 가능한 Datamart(community_dw_full.csv) 생성 성공.

📈 Tableau 대시보드 구성

대시보드는 다음 4개의 시트로 구성했습니다.

✔ 1) DAU — Daily Active Users

날짜별로 활동한 User 수 집계

시간대별 사용자 활성도 확인 가능

✔ 2) WAU — Weekly Active Users

주 단위 고유 사용자 수 집계

서비스 리텐션 확인

✔ 3) MAU — Monthly Active Users

월별 활성 사용자수

장기 사용자 잔존 파악

✔ 4) KPI 카드

대시보드 상단에 텍스트 형태의 KPI를 배치:

총 사용자 수

이번 주 활성 사용자 수(WAU)

이번 달 활성 사용자 수(MAU)

📌 예시 출력:
- 총 사용자: 200명
- 이번 주 활성 사용자(WAU): 9명
- 이번 달 활성 사용자(MAU): 199명

🧠 인사이트 요약

✔ 초반 1~2주 동안 신규 사용자 유입이 크게 늘었음
✔ WAU는 9명으로 상대적으로 낮아 꾸준한 활동 유도 필요
✔ MAU는 199명으로 매우 높아, 월 단위 잔존율은 양호함
✔ 특정 날짜에 행동 Log가 집중되는 경향이 보임 (콘텐츠 이벤트/노출 영향 가능)

🚀 향후 발전 방향

사용자 세그먼트(신규/휴면/충성) 분류 기능 추가

행동 유형별 분석(좋아요·댓글·조회 등) 시각화

Tableau 필터 기능 고도화(성별/나이대별 분석)

시계열 기반 예측 모델 적용 가능 (Prophet 등)

📝 라이선스

본 프로젝트의 데이터는 학습 목적의 더미 데이터이며,
자유롭게 참고 및 수정하여 사용할 수 있습니다.