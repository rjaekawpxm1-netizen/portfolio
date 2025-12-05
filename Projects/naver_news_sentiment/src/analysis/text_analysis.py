import os
import re
import pandas as pd

########################################
# 0. 경로 설정
########################################

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # .../src/analysis
SRC_DIR = os.path.dirname(BASE_DIR)                     # .../src
ROOT_DIR = os.path.dirname(SRC_DIR)                     # .../naver_news_sentiment

PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")



########################################
# 1. 데이터 불러오기
########################################

def load_comments_with_sentiment(csv_name="comments_with_sentiment.csv"):
    csv_path = os.path.join(PROCESSED_DIR, csv_name)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"{csv_path} 파일을 찾을 수 없습니다.")

    df = pd.read_csv(csv_path)
    if "comment" not in df.columns and "comment_clean" not in df.columns:
        raise KeyError("데이터에 'comment' 또는 'comment_clean' 컬럼이 없습니다.")
    return df


########################################
# 2. 욕설/혐오 관련 키워드 리스트 (간단 버전)
########################################

HATE_WORDS = [
    "병신", "멍청이", "개같", "개새", "씨발", "시발", "ㅅㅂ", "ㅂㅅ",
    "또라이", "정신병자", "미친놈", "멍청한", "죽어라", "죽어버려",
    "꺼져", "꺼지세요", "인간도 아님", "인간 이하",
    "틀딱", "한남", "한녀", "노답", "인생망함",
]

# 필요하면 나중에 카테고리별로 나눌 수도 있음 (욕설 / 비하 / 혐오 등)


########################################
# 3. 전처리 (선택)
########################################

def basic_clean(text: str) -> str:
    text = str(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


########################################
# 4. 한 문장에 대해 악성 여부 판정
########################################

def rule_based_hate(text: str):
    """
    반환값: (is_hate, hate_type)
      - is_hate: 0 또는 1
      - hate_type: 문자열 (예: '욕설/비하') 또는 빈 문자열
    """
    if not isinstance(text, str) or text.strip() == "":
        return 0, ""

    t = text

    for w in HATE_WORDS:
        if w in t:
            return 1, "욕설/비하"

    return 0, ""


########################################
# 5. 전체 데이터에 악성 댓글 라벨 달기
########################################

def add_hate_labels(df: pd.DataFrame) -> pd.DataFrame:
    # 우선 분석에 쓸 컬럼 선택
    if "comment_clean" in df.columns:
        target_col = "comment_clean"
    else:
        target_col = "comment"

    is_hate_list = []
    hate_type_list = []

    for i, text in enumerate(df[target_col]):
        if (i + 1) % 20 == 0:
            print(f"  → {i+1}개 악성 여부 처리 완료")

        is_hate, hate_type = rule_based_hate(text)
        is_hate_list.append(is_hate)
        hate_type_list.append(hate_type)

    df["is_hate"] = is_hate_list      # 0/1
    df["hate_type"] = hate_type_list  # 문자열 (없으면 "")

    return df


########################################
# 6. 메인 실행
########################################

def main():
    print("📂 감정 분석이 포함된 댓글 데이터 불러오는 중...")
    df = load_comments_with_sentiment("comments_with_sentiment.csv")
    print(f"불러온 데이터 수: {len(df)}")

    print("⚙️ 악성 댓글(Hate) 라벨링 시작...")
    df_with_hate = add_hate_labels(df)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    output_path = os.path.join(PROCESSED_DIR, "comments_with_sentiment_hate.csv")
    df_with_hate.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("🎉 악성 댓글 라벨링 완료!")
    print(f"저장 위치: {output_path}")


if __name__ == "__main__":
    main()
