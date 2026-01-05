import pandas as pd

def load_accidents_csv(path):
    # 1) 인코딩 자동 처리
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="cp949")

    # 2) 컬럼명에서 공백 / BOM 같은 숨은 문자 제거
    df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
    print("정리된 컬럼:", list(df.columns))  # 확인용

    # 3) 한국어 → 영어 컬럼 매핑
    column_map = {
        "구": "region",
        "사고건수": "accident_count",
        "사망자수": "death_count",
        "부상신고자수": "injury_report_count",
        "사상자수": "casualty_count",
        "사고 1건당 사상자수": "casualties_per_accident",
    }

    df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})

    # 4) 최소 필요한 컬럼 체크
    required_cols = ["region", "accident_count", "death_count", "casualty_count"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"요약 CSV 컬럼이 부족함: {missing} / 필요: {required_cols}")

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
