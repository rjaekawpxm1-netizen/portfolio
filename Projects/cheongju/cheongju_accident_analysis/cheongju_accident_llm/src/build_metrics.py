import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "out"

def to_int(x):
    # "1,234" 같은 문자열도 숫자로 안전하게
    if pd.isna(x):
        return 0
    if isinstance(x, str):
        x = x.replace(",", "").strip()
    return int(float(x))

def main():
    OUT.mkdir(exist_ok=True)

    cheongju = pd.read_csv(DATA / "cheongju_accident_summary.csv")
    regions = pd.read_csv(DATA / "accidents_summary_by_region.csv")

    # ---- 청주시 1행 요약 ----
    cj = cheongju.iloc[0].to_dict()
    cheongju_counts = {
        "사망": to_int(cj.get("사망자수")),
        "중상": to_int(cj.get("중상자수")),
        "경상": to_int(cj.get("경상자수")),
        "부상신고": to_int(cj.get("부상신고자수")),
    }
    cheongju_total_victims = sum(cheongju_counts.values())

    # ---- 전국 합계(시군구 전체 합) ----
    # 컬럼명이 정확히 일치해야 함: 사망자수/중상자수/경상자수/부상신고자수
    national_counts = {
        "사망": to_int(regions["사망자수"].sum()),
        "중상": to_int(regions["중상자수"].sum()),
        "경상": to_int(regions["경상자수"].sum()),
        "부상신고": to_int(regions["부상신고자수"].sum()),
    }
    national_total_victims = sum(national_counts.values())

    # ---- 비율 계산 ----
    def pct_dict(counts: dict, total: int):
        return {k: (v / total if total else 0) for k, v in counts.items()}

    payload = {
        "기간": "데이터 파일 기준(기간 컬럼 없으면 생략 가능)",
        "청주시": {
            "사고건수": to_int(cj.get("사고건수")),
            "사상자합계": to_int(cj.get("사상자수_합계")),
            "심각도_건수": cheongju_counts,
            "심각도_비율": pct_dict(cheongju_counts, cheongju_total_victims),
        },
        "전국": {
            "사상자합계_추정(사망+중상+경상+부상신고)": national_total_victims,
            "심각도_건수": national_counts,
            "심각도_비율": pct_dict(national_counts, national_total_victims),
        },
        "비교_포인트": {
            "청주_vs_전국_심각도비율_차이(청주-전국)": {
                k: pct_dict(cheongju_counts, cheongju_total_victims)[k] - pct_dict(national_counts, national_total_victims)[k]
                for k in cheongju_counts.keys()
            }
        }
    }

    (OUT / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Saved:", OUT / "metrics.json")

if __name__ == "__main__":
    main()
