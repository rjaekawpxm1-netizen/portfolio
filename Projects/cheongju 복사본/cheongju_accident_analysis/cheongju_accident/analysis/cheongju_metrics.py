import os
import pandas as pd

def analyze_cheongju_metrics(
    processed_path: str = os.path.join("data", "processed", "accidents_clean.csv")
):
    """
    청주시만 뽑아서 '위험도/치명도' 지표 만들고,
    전국 합계/평균과 비교한 테이블을 반환 + 저장용 데이터프레임 생성
    """
    df = pd.read_csv(processed_path)

    # 안전하게 숫자 컬럼 보정
    num_cols = ["사고건수", "사망자수", "중상자수", "경상자수", "부상신고자수"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # 청주시 행만 필터 (데이터에 "청주시"로 들어있다고 가정)
    cheongju = df[df["시군구"].astype(str).str.contains("청주", na=False)].copy()

    # 혹시 "청주시"가 딱 하나로 들어가면 아래처럼 더 강하게 좁혀도 됨
    # cheongju = df[df["시군구"].astype(str).str.strip().eq("청주시")].copy()

    if cheongju.empty:
        raise ValueError("청주시 데이터가 0건입니다. '시군구' 값에 청주가 포함되는지 CSV를 확인하세요.")

    # 합계 기반 지표 (청주시 합계 1행)
    cj_sum = cheongju[num_cols].sum(numeric_only=True)

    cj_acc = cj_sum.get("사고건수", 0)
    cj_death = cj_sum.get("사망자수", 0)
    cj_serious = cj_sum.get("중상자수", 0)
    cj_minor = cj_sum.get("경상자수", 0)
    cj_report = cj_sum.get("부상신고자수", 0)

    cj_casualties = cj_death + cj_serious + cj_minor + cj_report

    cheongju_metrics = pd.DataFrame([{
        "지역": "청주시",
        "사고건수": cj_acc,
        "사망자수": cj_death,
        "중상자수": cj_serious,
        "경상자수": cj_minor,
        "부상신고자수": cj_report,
        "사상자수(합)": cj_casualties,
        "사고당_사상자": (cj_casualties / cj_acc) if cj_acc else 0,
        "사고당_사망자": (cj_death / cj_acc) if cj_acc else 0,
        "사고당_중상자": (cj_serious / cj_acc) if cj_acc else 0,
        "사망비율(사상자대비)": (cj_death / cj_casualties) if cj_casualties else 0,
    }])

    # 전국 지표 (전체 합계 1행)
    kr_sum = df[num_cols].sum(numeric_only=True)
    kr_acc = kr_sum.get("사고건수", 0)
    kr_death = kr_sum.get("사망자수", 0)
    kr_serious = kr_sum.get("중상자수", 0)
    kr_minor = kr_sum.get("경상자수", 0)
    kr_report = kr_sum.get("부상신고자수", 0)
    kr_casualties = kr_death + kr_serious + kr_minor + kr_report

    korea_metrics = pd.DataFrame([{
        "지역": "전국(합계)",
        "사고건수": kr_acc,
        "사망자수": kr_death,
        "중상자수": kr_serious,
        "경상자수": kr_minor,
        "부상신고자수": kr_report,
        "사상자수(합)": kr_casualties,
        "사고당_사상자": (kr_casualties / kr_acc) if kr_acc else 0,
        "사고당_사망자": (kr_death / kr_acc) if kr_acc else 0,
        "사고당_중상자": (kr_serious / kr_acc) if kr_acc else 0,
        "사망비율(사상자대비)": (kr_death / kr_casualties) if kr_casualties else 0,
    }])

    compare = pd.concat([cheongju_metrics, korea_metrics], ignore_index=True)

    return cheongju_metrics, compare
