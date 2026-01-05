import pandas as pd

REQUIRED_COLS = ["date", "time", "region", "road_type", "weather", "severity", "accident_type"]

def load_accidents_csv(path):
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="cp949")

    # (선택) 실제 컬럼명 확인용
    print("CSV columns:", list(df.columns))
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    
    
    
    if missing:
        raise ValueError(f"CSV 컬럼이 부족함: {missing} / 필요: {REQUIRED_COLS}")

    # 파생 컬럼
    df["datetime"] = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str), errors="coerce")
    df["hour"] = df["datetime"].dt.hour
    df["month"] = df["datetime"].dt.month
    return df

def basic_summary(df: pd.DataFrame) -> str:
    # 간단 통계 텍스트 요약(LLM에 같이 넣기 좋게)
    top_region = df["region"].value_counts().head(5).to_dict()
    top_road = df["road_type"].value_counts().head(5).to_dict()
    top_weather = df["weather"].value_counts().head(5).to_dict()
    top_type = df["accident_type"].value_counts().head(5).to_dict()
    top_hour = df["hour"].value_counts().sort_index().tail(6).to_dict()

    lines = []
    lines.append(f"- 총 사고 건수: {len(df)}")
    lines.append(f"- 지역 Top5: {top_region}")
    lines.append(f"- 도로유형 Top5: {top_road}")
    lines.append(f"- 날씨 Top5: {top_weather}")
    lines.append(f"- 사고유형 Top5: {top_type}")
    lines.append(f"- 시간대 분포(일부): {top_hour}")
    return "\n".join(lines)
