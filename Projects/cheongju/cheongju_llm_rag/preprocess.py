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

def basic_summary(df):
    stats = {}

    # 1) 전체 사고/사망/사상자 합계
    if "accident_count" in df.columns:
        stats["total_accidents"] = int(df["accident_count"].sum())
    if "death_count" in df.columns:
        stats["total_deaths"] = int(df["death_count"].sum())
    if "casualty_count" in df.columns:
        stats["total_casualties"] = int(df["casualty_count"].sum())

    # 2) 사고건수 기준 상위 5개 구
    if "region" in df.columns and "accident_count" in df.columns:
        top_regions = (
            df.sort_values("accident_count", ascending=False)
              .head(5)[["region", "accident_count"]]
              .to_dict(orient="records")
        )
        stats["top_regions"] = top_regions

    # 3) 상세 사고 데이터가 있을 때만 계산 (없어도 에러 안 나게)
    stats["top_road"] = (
        df["road_type"].value_counts().head(5).to_dict()
        if "road_type" in df.columns
        else {}
    )

    stats["top_weather"] = (
        df["weather"].value_counts().head(5).to_dict()
        if "weather" in df.columns
        else {}
    )

    stats["top_accident_type"] = (
        df["accident_type"].value_counts().head(5).to_dict()
        if "accident_type" in df.columns
        else {}
    )

    return stats

