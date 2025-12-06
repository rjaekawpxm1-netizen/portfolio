import os
import pandas as pd
import streamlit as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(ROOT, "data", "processed")

CSV_HATE = "comments_with_sentiment_hate.csv"
CSV_SENT = "comments_with_sentiment.csv"


def normalize_sentiment(raw):
    if not isinstance(raw, str):
        return "중립"

    pos = ["긍정", "찬성", "예", "좋", "괜찮"]
    neg = ["부정", "반대", "싫", "나쁘", "짜증", "화"]

    if any(k in raw for k in pos):
        return "긍정"
    if any(k in raw for k in neg):
        return "부정"
    return "중립"


@st.cache_data
def load_data():
    hate_path = os.path.join(PROCESSED, CSV_HATE)
    sent_path = os.path.join(PROCESSED, CSV_SENT)

    if os.path.exists(hate_path):
        df = pd.read_csv(hate_path)
    elif os.path.exists(sent_path):
        df = pd.read_csv(sent_path)
    else:
        raise FileNotFoundError("processed 폴더에 결과 CSV가 없습니다.")

    # UI 감정 컬럼
    df["sentiment_ui"] = df["sentiment"].apply(normalize_sentiment)

    # 날짜 컬럼 감지
    for col in ["created_at", "reg_time", "datetime", "date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            df["date_for_trend"] = df[col].dt.date
            break

    return df
