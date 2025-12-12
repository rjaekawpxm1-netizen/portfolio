import os
import pandas as pd


def analyze_cheongju_only(
    input_path: str = os.path.join("data", "processed", "accidents_clean.csv"),
    keyword: str = "청주"
):
    """
    accidents_clean.csv에서 '시군구'에 keyword(기본: '청주')가 포함된 행만 추출해
    청주시 지표를 계산하고, 청주시 데이터프레임과 요약(1행 DF)을 반환한다.
    """

    df = pd.read_csv(input_path)

    # 안전장치: 컬럼 확인
    required_cols = ["시군구", "사고건수", "사망자수", "부상신고자수"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(f"필수 컬럼이 없습니다: {missing} / 현재 컬럼: {df.columns.tolist()}")

    # 청주시 필터링 (정확히 '청주시' 일 수도, '청주시 흥덕구' 같은 형태일 수도 있어서 contains 사용)
    cheongju = df[df["시군구"].astype(str).str.contains(keyword, na=False)].copy()

    # 청주시 데이터가 없으면 바로 알려주기
    if cheongju.empty:
        raise ValueError(f"'{keyword}'가 포함된 시군구가 없습니다. 시군구 예시: {df['시군구'].head(10).tolist()}")

    # 숫자형 변환(혹시 문자열이면)
    for col in ["사고건수", "사망자수", "부상신고자수"]:
        cheongju[col] = pd.to_numeric(cheongju[col], errors="coerce")

    cheongju = cheongju.dropna(subset=["사고건수", "사망자수", "부상신고자수"])

    # 요약 지표 계산
    accidents = int(cheongju["사고건수"].sum())
    deaths = int(cheongju["사망자수"].sum())
    injuries_reported = int(cheongju["부상신고자수"].sum())
    casualty_total = deaths + injuries_reported

    death_rate_per_1000_acc = round((deaths / accidents) * 1000, 3) if accidents > 0 else 0
    casualty_per_acc = round((casualty_total / accidents), 4) if accidents > 0 else 0

    cheongju_summary = pd.DataFrame([{
        "지역": "청주시(필터:contains '청주')",
        "사고건수": accidents,
        "사망자수": deaths,
        "부상신고자수": injuries_reported,
        "사상자수(사망+부상신고)": casualty_total,
        "사고 1건당 사상자수": casualty_per_acc,
        "사고 1000건당 사망자수": death_rate_per_1000_acc
    }])

    return cheongju, cheongju_summary
