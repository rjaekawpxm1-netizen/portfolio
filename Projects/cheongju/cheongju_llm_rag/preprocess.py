import pandas as pd

# ------------------------------------------------------------------
# CSV 로딩 함수
#  - 동/위도·경도 집계 (시도코드명, 시군구명, 읍면동명, 사고건수, 위도, 경도)
#  - 구 단위 요약 (구, 사고건수, 사망자수, 부상신고자수, 사상자수...)
#  - 요일·시간대·월별 요약 (요일별(1), 시간대별(1), 월별(1), 2024, 2024.1, 2024.2)
#  - 나중에 상세사고 데이터(발생일자 등)도 확장 가능
# ------------------------------------------------------------------
def load_accidents_csv(path):
    # 1) 인코딩 자동 처리
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="cp949")

    # 2) 컬럼명 정리 (공백, BOM 제거)
    df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
    print("정리된 컬럼:", list(df.columns))

    cols = set(df.columns)

    # ==========================
    # A. 구 단위 요약 데이터 모드
    #    예: ['구', '사고건수', '사망자수', '부상신고자수', '사상자수', ...]
    # ==========================
    if "구" in cols and "사고건수" in cols and "읍면동명" not in cols:
        df = df.rename(
            columns={
                "구": "region",
                "사고건수": "accident_count",
                "사망자수": "death_count",
                "부상신고자수": "injury_report_count",
                "사상자수": "casualty_count",
                "사고 1건당 사상자수": "casualties_per_accident",
            }
        )

        # 필수: region, accident_count
        if "region" not in df.columns:
            first_col = df.columns[0]
            df["region"] = df[first_col].astype(str)
        if "accident_count" not in df.columns:
            raise ValueError("구 단위 요약 CSV에서 accident_count(사고건수)를 찾지 못함")

        df["mode"] = "district_summary"
        return df

    # ==========================
    # B. 동 단위 + 위도·경도 집계 모드
    #    예: ['시도코드명', '시군구명', '읍면동명', '사고건수', '위도', '경도']
    # ==========================
    if {"시도코드명", "시군구명", "읍면동명", "사고건수"}.issubset(cols):
        df = df.rename(
            columns={
                "시도코드명": "province",
                "시군구명": "district",
                "읍면동명": "subdistrict",
                "사고건수": "accident_count",
                "위도": "lat",
                "경도": "lon",
            }
        )

        # region = 시군구명 + 읍면동명 (예: "흥덕구 강서1동")
        df["region"] = df["district"].astype(str) + " " + df["subdistrict"].astype(str)

        df["mode"] = "geo_summary"
        return df

    # ==========================
    # C. 요일·시간대·월별 집계 모드
    #    예: ['요일별(1)', '시간대별(1)', '월별(1)', '2024', '2024.1', '2024.2']
    # ==========================
    if {"요일별(1)", "시간대별(1)", "월별(1)", "2024"}.issubset(cols):
        # 첫 행이 헤더 내용인 경우 제거
        # (요일별(1) == '요일별(1)' 이고 2024 == '사고건수 (건)' 인 행)
        try:
            if str(df.iloc[0]["요일별(1)"]) == "요일별(1)":
                df = df.iloc[1:].reset_index(drop=True)
        except Exception:
            pass

        df = df.rename(
            columns={
                "요일별(1)": "weekday",
                "시간대별(1)": "time_band",
                "월별(1)": "month",
                "2024": "accident_count",   # 사고건수
                "2024.1": "death_count",    # 사망자수
                "2024.2": "injury_count",   # 부상자수
            }
        )

        # 숫자형으로 변환
        for col in ["accident_count", "death_count", "injury_count"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df["mode"] = "time_summary"
        return df

    # ==========================
    # D. (옵션) 상세 사고 데이터 모드
    #    발생일자, 시군구, 도로형태, 기상상태, 사고유형 등 있는 경우
    # ==========================
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
        # severity(중상/경상 등)는 데이터 구조 보고 나중에 추가해도 됨
    }
    df = df.rename(columns={k: v for k, v in column_map_detail.items() if k in df.columns})

    # 상세 모드에서 최소로 요구할 컬럼 (너무 빡세게 안 함)
    required_detail = ["date", "time", "region"]
    missing = [c for c in required_detail if c not in df.columns]
    if missing:
        raise ValueError(f"인식할 수 없는 CSV 형식입니다. 최소 컬럼 부족: {missing}")

    df["mode"] = "detail"
    return df


# ------------------------------------------------------------------
# 기본 요약 통계
#  - summary 계열(mode == *_summary)은 사고건수/사망자 등 합계 위주
#  - detail 모드는 나중에 필요하면 확장
# ------------------------------------------------------------------
def basic_summary(df):
    stats = {}

    mode = df["mode"].iloc[0] if "mode" in df.columns else None
    if mode is None:
        if "accident_count" in df.columns:
            mode = "summary"
        else:
            mode = "detail"

    # ===== 요약 계열 모드 (구/동/요일·시간대) =====
    if mode in ["district_summary", "geo_summary", "time_summary", "summary"]:
        if "accident_count" in df.columns:
            stats["total_accidents"] = int(df["accident_count"].sum())

        if "death_count" in df.columns:
            stats["total_deaths"] = int(df["death_count"].sum())

        # casualty_count가 있으면 사용
        if "casualty_count" in df.columns:
            stats["total_casualties"] = int(df["casualty_count"].sum())

        # 1) 지역 기준 상위 5개 (구/동 단위)
        if "region" in df.columns and "accident_count" in df.columns:
            top_regions = (
                df.groupby("region")["accident_count"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
                .to_dict()
            )
            stats["top_regions"] = top_regions

        # 2) 요일 기준 상위 5개 (요일·시간대 CSV)
        if "weekday" in df.columns and "accident_count" in df.columns:
            top_weekdays = (
                df.groupby("weekday")["accident_count"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
                .to_dict()
            )
            stats["top_weekdays"] = top_weekdays

    # ===== detail 모드 (발생 일시/기상 등 상세데이터) =====
    else:
        # 필요하면 여기서 road_type, weather, accident_type 통계도 추가 가능
        if "road_type" in df.columns:
            stats["top_road"] = (
                df["road_type"].value_counts().head(5).to_dict()
            )
        else:
            stats["top_road"] = {}

        if "weather" in df.columns:
            stats["top_weather"] = (
                df["weather"].value_counts().head(5).to_dict()
            )
        else:
            stats["top_weather"] = {}

        if "accident_type" in df.columns:
            stats["top_accident_type"] = (
                df["accident_type"].value_counts().head(5).to_dict()
            )
        else:
            stats["top_accident_type"] = {}

    return stats
