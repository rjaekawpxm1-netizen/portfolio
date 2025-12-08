import os
import pandas as pd
import streamlit as st

# 현재 파일 기준 경로 계산
THIS_DIR = os.path.dirname(os.path.abspath(__file__))          # .../src/dashboard
SRC_DIR = os.path.dirname(THIS_DIR)                            # .../src
PROJECT_ROOT = os.path.dirname(SRC_DIR)                        # .../naver_news_sentiment

# 우리가 찾을 수 있는 processed 후보 경로 2곳
PROCESSED_DIR_CANDIDATES = [
    os.path.join(PROJECT_ROOT, "data", "processed"),           # 새 구조
    os.path.join(PROJECT_ROOT, "src", "data", "processed"),    # 예전 구조
]

CSV_HATE = "comments_with_sentiment_hate.csv"
CSV_SENT = "comments_with_sentiment.csv"


def normalize_sentiment(raw):
    """원본 감정 라벨을 긍정/중립/부정 3단계로 단순 매핑"""
    if not isinstance(raw, str):
        return "중립"

    pos = ["긍정", "찬성", "예", "좋", "괜찮", "호의", "좋아요", "좋네요"]
    neg = ["부정", "반대", "싫", "나쁘", "짜증", "화", "불만", "최악"]

    if any(k in raw for k in pos):
        return "긍정"
    if any(k in raw for k in neg):
        return "부정"
    return "중립"


def _find_existing_file():
    """
    후보 경로들(PROCESSED_DIR_CANDIDATES)에서
    comments_with_sentiment_hate.csv → 없으면 comments_with_sentiment.csv 순으로 찾는다.
    """
    tried_paths = []

    for base in PROCESSED_DIR_CANDIDATES:
        hate_path = os.path.join(base, CSV_HATE)
        sent_path = os.path.join(base, CSV_SENT)

        tried_paths.extend([hate_path, sent_path])

        if os.path.exists(hate_path):
            return hate_path, True, tried_paths   # (경로, hate파일인지, 시도경로리스트)
        if os.path.exists(sent_path):
            return sent_path, False, tried_paths

    return None, None, tried_paths


@st.cache_data
def load_data():
    csv_path, has_hate, tried_paths = _find_existing_file()

    if csv_path is None:
        # 어디를 찾았는지까지 같이 보여주기
        msg = "processed 폴더에 결과 CSV를 찾을 수 없습니다.\n\n시도한 경로:\n"
        msg += "\n".join(f"- {p}" for p in tried_paths)
        raise FileNotFoundError(msg)

    # 파일 로드
    df = pd.read_csv(csv_path)
    st.caption(f"✅ 불러온 파일: {os.path.basename(csv_path)}")

    # sentiment → 3단계 감정 라벨로 변환
    if "sentiment" in df.columns:
        df["sentiment_ui"] = df["sentiment"].apply(normalize_sentiment)
    else:
        df["sentiment_ui"] = "중립"

    # 날짜 컬럼 자동 감지 (그래프용)
    time_candidates = [
        "comment_created_at", "created_at", "reg_time", "reg_date",
        "written_at", "datetime", "date",
    ]
    for col in time_candidates:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            df["date_for_trend"] = df[col].dt.date
            break

    return df
