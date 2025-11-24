# 🤖 고객 이탈 예측 모델링 (Churn Prediction)

본 프로젝트는 Project 1(온라인 쇼핑몰 분석)에서 생성한 고객·주문 데이터를 활용하여  
고객의 **이탈 가능성(churn)** 을 예측하는 머신러닝 모델을 구축한 프로젝트이다.

---

## 1. 프로젝트 개요

전자상거래(E-Commerce) 환경에서 고객 이탈은 매출 감소로 직결되는 중요한 문제이다.  
본 프로젝트의 목표는 고객의 과거 구매 행동을 분석하여

> **“어떤 고객이 한 번만 구매하고 이탈할 가능성이 높은가?”**

를 예측하는 분류 모델을 만드는 것이다.

### 🎯 이탈 정의(Churn Definition)

- **총 주문 횟수 = 1회 → 이탈 고객 (churn_label = 1)**
- **총 주문 횟수 ≥ 2회 → 유지 고객 (churn_label = 0)**

즉, 1회성 구매 후 재구매가 없는 고객을 이탈 위험군으로 정의하였다.

---

## 2. 데이터 출처 및 전처리

- 데이터베이스: `shop.db`  
  - Project1(온라인 쇼핑몰 매출·고객 분석)에서 생성한 더미 쇼핑몰 DB  
  - 주요 테이블: `customers`, `orders`, `order_items`, `products`
- 전처리 노트북: `churn_data_preprocessing.ipynb`
- 최종 학습용 데이터셋: `data/churn_dataset.csv`

### 📦 Feature Engineering

`orders` 테이블을 기반으로 고객 단위로 다음과 같은 특징을 생성하였다.

| Feature             | 설명                                                   
|--------------------|--------------------------------------------------------
| customer_id         | 고객 ID                                               
| total_orders        | 총 주문 횟수 (paid 상태 주문 기준)                    
| first_order         | 첫 주문 일시                                          
| last_order          | 마지막 주문 일시                                      
| days_between        | 첫 주문~마지막 주문까지의 기간(일)                    
| avg_days_per_order  | 주문 간 평균 간격 (days_between / total_orders)      
| churn_label         | 1회 구매 고객=1(이탈), 2회 이상=0(유지)                

- 전체 샘플 수: **1,694명**
- 라벨 분포:
  - 유지 고객(0): **1,125명**
  - 이탈 고객(1): **569명**

---

## 3. 모델링

모델링은 `churn_modeling.ipynb`에서 진행하였다.

### 사용 알고리즘

1. **Logistic Regression**
   - 입력 변수 표준화(StandardScaler) 적용
   - 선형 모델을 이용한 baseline 성능 확인

2. **RandomForestClassifier**
   - 비선형 관계와 변수 간 상호작용까지 학습 가능한 트리 기반 앙상블 모델
   - Feature Importance를 활용해 중요한 행동 패턴 해석

### 학습 및 평가

- Train/Test Split: 8:2
- 평가 지표: **Accuracy, F1-score**

Random Forest 기준 결과:

- **Accuracy: 1.00**
- **F1-score: 1.00**

> 이탈 정의가 “1회 구매 고객”으로 명확하고,  
> 핵심 Feature인 `total_orders`와 라벨이 강하게 연관되어 있어  
> 모델이 모든 사례를 완벽하게 분류할 수 있었다.

---

## 4. Feature Importance 분석

Random Forest의 변수 중요도는 다음과 같다.

| Feature            | Importance |
|-------------------|-----------:|
| total_orders       | 0.344      |
| days_between       | 0.343      |
| avg_days_per_order | 0.313      |

### 해석

- **total_orders**  
  - 이탈 라벨이 “1회 구매” 기준으로 정의되어 있어,  
    주문 횟수가 가장 직접적인 판단 기준이 된다.
- **days_between**  
  - 주문 간 간격이 있는지 여부는 재구매 여부와 밀접한 관련이 있음.
- **avg_days_per_order**  
  - 고객의 구매 패턴이 얼마나 규칙적인지, 재방문 주기를 파악할 수 있는 지표이다.

> 세 변수 모두 “얼마나 자주, 얼마나 오래, 얼마나 지속적으로 구매했는가”를 설명하는 지표로  
> 고객 이탈을 설명하는 데 중요한 역할을 한다.

---

## 5. 한계점 및 향후 개선 방향

현재 모델은 **1회 vs 2회 이상 구매 여부**만으로 이탈을 정의했기 때문에,  
실제 서비스 환경에서의 “진짜 이탈”을 완전히 반영한다고 보기 어렵다.

향후 개선 아이디어:

1. **이탈 정의 고도화**
   - “마지막 구매 후 90일 이상 재구매가 없는 고객” 등 기간 기반 정의 적용
2. **고객 속성 추가**
   - 성별, 연령대, 지역, 선호 결제수단, 디바이스 등 추가 Feature 반영
3. **행동 기반 지표 확장**
   - 월별 활동 여부, 최근 30일/90일 구매 유무, 구매 금액 구간 등

---

## 6. 주요 파일 구조

```text
02_Churn_Prediction/
 ├─ data/
 │   └─ churn_dataset.csv         # 최종 학습용 데이터셋
 ├─ images/
 │   └─ feature_importance.png    # 변수 중요도 시각화
 ├─ churn_data_preprocessing.ipynb  # 전처리 및 라벨링
 ├─ churn_modeling.ipynb            # 모델 학습 및 평가
 └─ README.md









## 🛠 Troubleshooting Log

### 1) SQLite DB 파일이 여러 개 존재하는 문제

**문제 상황**  
- `shop`, `shop.db` 파일이 서로 다른 폴더에 여러 개 존재했고  
  특히 크기가 0KB인 `shop` 파일이 자동으로 생성되면서  
  `no such table: orders` 에러가 지속적으로 발생하였다.

**원인**  
- `sqlite3.connect("shop")` 로 연결할 경우,  
  해당 이름의 파일이 없으면 SQLite가 **새로운 빈 DB 파일을 생성**한다.  
- 이로 인해 실제 데이터가 들어 있는 `shop.db`가 아니라,  
  비어 있는 `shop` 파일을 읽게 되었다.

**해결 방법**  
- 프로젝트에서 사용할 DB 파일을 `shop.db`로 고정하고,  
  모든 노트북에서 `sqlite3.connect("shop.db")` 로 통일하였다.
- 0KB인 `shop` 파일은 모두 삭제하였다.

---

### 2) orders 테이블은 있는데 JOIN 결과가 0건이 나오는 문제

**문제 상황**  
- `SELECT ... FROM orders o JOIN order_items oi ...` 쿼리를 실행했을 때  
  `orders`에는 5,000건이 있음에도 불구하고 결과 DataFrame의 shape가 `(0, n)` 으로 나왔다.
- 이로 인해 `churn_dataset.csv`가 헤더만 있는 빈 파일로 저장되었고,  
  `train_test_split`에서 `n_samples=0` 에러가 발생했다.

**원인**  
- 사용하는 `shop.db`에 `order_items` 데이터가 제대로 들어 있지 않은 상태에서  
  INNER JOIN을 수행하여 결과가 모두 필터링되었다.

**해결 방법**  
- 이탈 예측에 필수적인 정보는 `orders`만으로도 충분하다고 판단하고,  
  전처리 쿼리에서 `order_items` JOIN을 제거하였다.
- 금액 정보 대신 주문 횟수와 기간(day_between, avg_days_per_order)에 집중하는 Feature Set으로 수정하였다.

---

### 3) 비어 있는 CSV 파일로 인한 모델링 오류

**문제 상황**  
- `data/churn_dataset.csv`가 비어 있는 상태에서  
  모델링 노트북에서 `pd.read_csv` 후 `train_test_split`을 수행해  
  `ValueError: n_samples=0` 에러가 발생했다.

**원인**  
- 앞선 JOIN 문제로 전처리 단계에서 생성된 DataFrame이 0행이었음에도  
  그대로 CSV를 저장했기 때문이다.

**해결 방법**  
- 전처리 노트북에서 `df.shape`를 먼저 확인하는 습관을 들였고,  
  쿼리와 Feature Engineering을 수정한 뒤  
  다시 `churn_dataset.csv`를 생성하여 문제를 해결하였다.

---

### 4) 교훈

- **DB 연결 경로와 파일 크기를 항상 확인할 것**
  - `os.getcwd()`, `os.listdir()`, `os.path.getsize()` 로 작업 디렉토리와 파일 상태를 체크
- **JOIN 사용 시 결과 row 수(df.shape)를 반드시 확인할 것**
- **중간 산출물(CSV 등)을 활용하는 모델링에서는 전처리 → 모델링 흐름을 반복적으로 검증할 것**
