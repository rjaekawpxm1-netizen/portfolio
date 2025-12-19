import pandas as pd
import os

def analyze_cheongju_only():
    print("[INFO] 청주시 분리 분석 시작")

    input_path = os.path.join("data", "processed", "accidents_clean.csv")
    df = pd.read_csv(input_path)

    # 청주시 데이터만 필터링
    cheongju_df = df[df["시군구"].str.contains("청주시")].copy()

    print(f"[INFO] 청주시 데이터 건수: {len(cheongju_df)}")

    # 주요 지표 계산
    summary = {
        "사고건수_합계": cheongju_df["사고건수"].sum(),
        "사망자수_합계": cheongju_df["사망자수"].sum(),
        "중상자수_합계": cheongju_df.get("중상자수", pd.Series()).sum(),
        "경상자수_합계": cheongju_df.get("경상자수", pd.Series()).sum(),
        "부상신고자수_합계": cheongju_df["부상신고자수"].sum(),
    }

    summary_df = pd.DataFrame([summary])

    output_path = os.path.join("data", "reports", "cheongju_detail_summary.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    summary_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"[INFO] 청주시 상세 요약 저장 → {output_path}")

    return cheongju_df, summary_df
