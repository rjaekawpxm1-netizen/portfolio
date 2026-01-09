import re
import pandas as pd
import os

########################################
# 0. 경로 설정 (추가)
########################################

# sentiment_analysis.py 파일이 있는 폴더
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # .../src/analysis
# src 폴더
SRC_DIR = os.path.dirname(BASE_DIR)                     # .../src
# 프로젝트 최상위 폴더 (src의 상위)
ROOT_DIR = os.path.dirname(SRC_DIR)                     # .../project

RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")


########################################
# 1. 데이터 불러오기
########################################

def load_comments(csv_name="comments_selenium.csv"):
    csv_path = os.path.join(RAW_DIR, csv_name)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"{csv_path} 파일을 찾을 수 없습니다.")
    
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["comment"])
    return df


########################################
# 2. 텍스트 전처리 함수
########################################

def clean_text(text: str) -> str:
    text = str(text)
    # 너무 과한 필터링은 피하고, 공백만 정리
    text = re.sub(r"\s+", " ", text).strip()
    return text


########################################
# 3. 간단한 한국어 감정 사전 정의
########################################

POSITIVE_WORDS = [
    "좋다", "좋아요", "좋네요", "최고", "굿", "행복", "기쁘", "맛있",
    "따뜻하", "따숩", "괜찮다", "즐겁", "재밌", "대박", "사랑", "다행",
]

NEGATIVE_WORDS = [
    "싫다", "별로", "최악", "짜증", "화나", "화가", "불편", "불만",
    "추워", "추움", "춥다", "더워", "더움", "춥네요", "춥노",
    "실망", "끔찍", "노답", "개판", "엉망", "우울", "역겹",
    "곤두박질", "떨어지겠", "안 좋", "안좋", "나쁘", "차갑",
]


########################################
# 4. 한 문장에 대해 감정 예측 (룰 기반)
########################################

def rule_based_sentiment(text: str) -> str:
    if not isinstance(text, str) or text.strip() == "":
        return "중립"

    t = text  # 한글이라 lower() 안 해도 됨
    pos_score = 0
    neg_score = 0

    for w in POSITIVE_WORDS:
        if w in t:
            pos_score += 1

    for w in NEGATIVE_WORDS:
        if w in t:
            neg_score += 1

    # 아무 단어도 안 걸리면 중립
    if pos_score == 0 and neg_score == 0:
        return "중립"

    if pos_score > neg_score:
        return "긍정"
    elif neg_score > pos_score:
        return "부정"
    else:
        return "중립"


########################################
# 5. 전체 데이터에 감정 라벨 달기
########################################

def add_sentiment_labels(df):
    df["comment_clean"] = df["comment"].apply(clean_text)

    sentiments = []
    for i, text in enumerate(df["comment_clean"]):
        if (i + 1) % 20 == 0:
            print(f"  → {i+1}개 처리 완료")
        label = rule_based_sentiment(text)
        sentiments.append(label)

    df["sentiment"] = sentiments
    return df


########################################
# 6. 메인 실행
########################################

if __name__ == "__main__":
    # 1) 데이터 불러오기
    df = load_comments("comments_selenium.csv")
    print(f"📂 불러온 댓글 수: {len(df)}")

    # 2) 감정 라벨링
    df_with_sentiment = add_sentiment_labels(df)

    # 3) 결과 저장
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    output_path = os.path.join(PROCESSED_DIR, "comments_with_sentiment.csv")
    df_with_sentiment.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("🎉 감정 분석(룰 기반) 완료!")
    print(f"저장 위치: {output_path}")
