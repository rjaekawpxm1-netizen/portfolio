import pandas as pd

# -----------------------
# CSV 로딩 함수
#  - 상세 사고 데이터든
#  - "구 요약 데이터"든
# 둘 다 처리 가능하게 설계
# -----------------------
def load_accidents_csv(path):
    # 1) 인코딩 자동 처리
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="cp949")

    # 2) 컬럼명 정리 (공백, BOM 제거)
    df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
    print("정리된 컬럼:", list(df.columns))

    cols = list(df.columns)

    # ==========================
    # A. "구 요약 데이터" 모드
    #    예: ['구', '사고건수', '사망자수', ...]
    # ==========================
    if "구" in cols or "사고건수" in cols:
        column_map = {
            "구": "region",
            "사고건수": "accident_count",
            "사망자수": "death_count",
            "부상신고자수": "injury_report_count",
            "사상자수": "casualty_count",
            "사고 1건당 사상자수": "casualties_per_accident",
        }
        df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})

        # 혹시라도 region이 안 만들어졌으면 첫 번째 컬럼을 region으로 사용
        if "region" not in df.columns:
            first_col = df.columns[0]
            df["region"] = df[first_col].astype(str)

        required_summary = ["region", "accident_count", "death_count", "casualty_count"]
        missing = [c for c in required_summary if c not in df.columns]
        if missing:
            raise ValueError(f"요약 CSV 컬럼이 부족함: {missing} / 필요: {required_summary}")

        df["mode"] = "summary"
        return df

    # ==========================
    # B. 상세 사고 데이터 모드
    #    (date, time, region, road_type, weather, severity, accident_type 등 있는 경우)
    # ==========================
    DETAIL_REQUIRED = [
        "date",
        "time",
        "region",
        "road_type",
        "weather",
        "severity",
        "accident_type",
    ]

    column_map_detail = {
        "발생일자": "date",
        "발생일시": "date",
        "발생시간": "time",
        "시군구": "region",
        "구": "region",
        "노면형태": "road_type",
        "도로형태": "road_type",
        "기상상태": "weather",
        "사고유형": "accident_type",
        "사고유형_대분류": "accident_type",
        # severity는 데이터 구조에 맞춰 나중에 추가 가능
    }

    df = df.rename(columns={k: v for k, v in column_map_detail.items() if k in df.columns})

    missing = [c for c in DETAIL_REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"CSV 컬럼이 부족함: {missing} / 필요: {DETAIL_REQUIRED}")

    df["mode"] = "detail"
    return df


# -----------------------
# 기본 요약 통계
#  - 요약모드(summary)면 구/사고건수 위주
#  - 상세모드(detail)면 road_type, weather 등도 포함
# -----------------------
def basic_summary(df):
    stats = {}

    # 1) 요약모드인지 상세모드인지 판단 (mode 컬럼이 없으면 추정)
    mode = df.get("mode", None)
    if mode is None:
        if "accident_count" in df.columns and "region" in df.columns:
            mode = "summary"
        else:
            mode = "detail"

    # ========= summary 모드 (구 요약 CSV) =========
    if mode == "summary":
        if "accident_count" in df.columns:
            stats["total_accidents"] = int(df["accident_count"].sum())
        if "death_count" in df.columns:
            stats["total_deaths"] = int(df["death_count"].sum())
        if "casualty_count" in df.columns:
            stats["total_casualties"] = int(df["casualty_count"].sum())

        if "region" in df.columns and "accident_count" in df.columns:
            top_regions = (
                df.sort_values("accident_count", ascending=False)
                  .head(5)[["region", "accident_count"]]
                  .to_dict(orient="records")
            )
            stats["top_regions"] = top_regions

        # summary에는 road_type / weather / accident_type 없을 수 있으니 빈 dict로
        stats["top_road"] = {}
        stats["top_weather"] = {}
        stats["top_accident_type"] = {}

    # ========= detail 모드 (상세 사고 데이터) =========
    else:
        # road_type / weather / accident_type 있을 때만 계산
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
