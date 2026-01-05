import os
import pandas as pd

# ------------------------------------------------------------------
# CSV 로딩 함수
#  - 동/위도·경도 집계 (시도코드명, 시군구명, 읍면동명, 사고건수, 위도, 경도)
#  - 구 단위 요약 (구, 사고건수, 사망자수, 부상신고자수, 사상자수...)
#  - 요일·시간대·월별 요약 (요일별(1), 시간대별(1), 월별(1), 2024, 2024.1, 2024.2)
#  - 나중에 상세사고 데이터(발생일자 등)도 확장 가능
# ------------------------------------------------------------------
def load_accidents_csv(file):
    # file: Streamlit UploadedFile 또는 파일 경로(str)

    # 1) 확장자 추출
    name = getattr(file, "name", None)
    if name is None:
        name = str(file)
    ext = os.path.splitext(name)[1].lower()

    # 2) 엑셀 / CSV 분기
    if ext in [".xlsx", ".xls"]:
        try:
            df = pd.read_excel(file)
        except EmptyDataError:
            raise ValueError("엑셀 파일 안에 데이터가 없어서 읽을 수 없어.")

    # 2) CSV 파일
    else:
        last_error = None
        for enc in ("utf-8-sig", "cp949"):
            try:
                df = pd.read_csv(file, encoding=enc)
                break
            except UnicodeDecodeError as e:
                last_error = e
                continue
            except EmptyDataError:
                raise ValueError("CSV 파일 안에 데이터가 없어서 읽을 수 없어.")
        else:
            # utf-8, cp949 둘 다 실패한 경우
            raise ValueError(f"CSV 인코딩을 인식하지 못했어. (마지막 에러: {last_error})")

    # 3) 컬럼명 정리 (이 아래부터는 네가 이미 쓰고 있는 모드 판별 / 매핑 로직)
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
        "시군구명": "region",
        "노면형태": "road_type",
        "도로형태": "road_type",
        "기상상태": "weather",
        "사고유형": "accident_type",
        "사고유형_대분류": "accident_type",
    }
    df = df.rename(columns={k: v for k, v in column_map_detail.items() if k in df.columns})

    # region 비슷한 컬럼이 하나도 없으면 그냥 안 만들어도 됨 (LLM에는 stats 거의 안 쓰여도 됨)
    if "region" not in df.columns:
        for cand in ["시군구", "구", "시군구명"]:
            if cand in df.columns:
                df["region"] = df[cand].astype(str)
                break

    # ❌ 더 이상 date/time/region 없다고 에러 내지 않고,
    #    그냥 "detail(또는 generic) 모드"로 받아들이기

    if "accident_count" not in df.columns:
        df["accident_count"] = 1

    df["mode"] = "detail"
    return df


# ------------------------------------------------------------------
# 기본 요약 통계
#  - summary 계열(mode == *_summary)은 사고건수/사망자 등 합계 위주
#  - detail 모드는 나중에 필요하면 확장
# ------------------------------------------------------------------
def basic_summary(df):
    stats = {}

    # 1) 모드, 행/열 정보
    mode = df["mode"].iloc[0] if "mode" in df.columns else "unknown"
    stats["mode"] = mode
    stats["rows"] = int(len(df))
    stats["columns"] = list(df.columns)

    # 2) 공통 지표: 사고/사망/사상자 합계 (있으면 계산)
    if "accident_count" in df.columns:
        stats["total_accidents"] = int(df["accident_count"].sum())

    if "death_count" in df.columns:
        stats["total_deaths"] = int(df["death_count"].sum())

    if "casualty_count" in df.columns:
        stats["total_casualties"] = int(df["casualty_count"].sum())

    # 3) 지역 기준 top5 (구/동/region 있는 경우)
    if "region" in df.columns and "accident_count" in df.columns:
        top_regions = (
            df.groupby("region")["accident_count"]
              .sum()
              .sort_values(ascending=False)
              .head(5)
              .to_dict()
        )
        stats["top_regions_by_accidents"] = top_regions

    # 4) 요일 기준 top5 (요일·시간대 파일일 때)
    if "weekday" in df.columns and "accident_count" in df.columns:
        top_weekdays = (
            df.groupby("weekday")["accident_count"]
              .sum()
              .sort_values(ascending=False)
              .head(5)
              .to_dict()
        )
        stats["top_weekdays_by_accidents"] = top_weekdays

    # 5) 상세 데이터에만 있는 애들(있을 때만 추가)
    for col, key in [
        ("road_type", "top_road"),
        ("weather", "top_weather"),
        ("accident_type", "top_accident_type"),
    ]:
          # 돌발 현황 파일 전용 요약 (컬럼이 있을 때만)
        if "돌발분류명" in df.columns:
          stats["top_incident_types"] = (
            df["돌발분류명"].value_counts().head(5).to_dict()
        )

        if "연월" in df.columns:
          stats["top_year_months"] = (
            df["연월"].value_counts().head(5).to_dict()
        )

    return stats
