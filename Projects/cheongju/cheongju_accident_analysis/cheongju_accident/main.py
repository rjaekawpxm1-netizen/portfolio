# cheongju/main.py

import os
import pandas as pd

from cheongju.api.fetch_accident_data import fetch_accident_data
from cheongju.preprocessing.clean_data import clean_accident_data
from cheongju.analysis.basic_stats import summarize_korea_and_cheongju
from cheongju.analysis.cheongju_only import analyze_cheongju_only
from cheongju.viz.make_plots import plot_accidents_by_region


def run_pipeline():
    # =========================
    # 폴더 준비
    # =========================
    os.makedirs(os.path.join("data", "raw"), exist_ok=True)
    os.makedirs(os.path.join("data", "processed"), exist_ok=True)
    os.makedirs(os.path.join("data", "reports"), exist_ok=True)

    # =========================
    # [1/5] 교통사고 데이터 수집 (odcloud)
    # =========================
    print("=== [1/5] 교통사고(odcloud) 데이터 수집 ===")
    df_raw = fetch_accident_data()

    raw_path = os.path.join("data", "raw", "accidents_raw.csv")
    df_raw.to_csv(raw_path, index=False, encoding="utf-8-sig")
    print(f"[INFO] 저장 완료 → {raw_path}")

    # =========================
    # [2/5] 데이터 전처리
    # =========================
    print("=== [2/5] 교통사고 데이터 전처리 ===")
    df_clean = clean_accident_data()

    processed_path = os.path.join("data", "processed", "accidents_clean.csv")
    df_clean.to_csv(processed_path, index=False, encoding="utf-8-sig")
    print(f"[INFO] 전처리 완료 → {processed_path}")

    # =========================
    # [3/5] 기초 통계 분석 (전국 vs 청주시)
    # =========================
    print("=== [3/5] 기초 통계 분석(전국/청주시 비교) ===")
    df_summary, cheongju_df, cheongju_rank = summarize_korea_and_cheongju()

    summary_path = os.path.join("data", "reports", "accidents_summary_by_region.csv")
    cheongju_path = os.path.join("data", "reports", "cheongju_accident_summary.csv")

    df_summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    cheongju_df.to_csv(cheongju_path, index=False, encoding="utf-8-sig")

    print(f"[INFO] 전국 요약 저장 → {summary_path}")
    print(f"[INFO] 청주시 요약 저장 → {cheongju_path}")
    print(f"[INFO] 청주시 전국 순위: {cheongju_rank}위")

    # =========================
    # [4/5] 청주시 단독 분석
    # =========================
    print("=== [4/5] 청주시 분리 분석 ===")
    cheongju_rows, cheongju_summary = analyze_cheongju_only()

    cheongju_only_path = os.path.join("data", "reports", "cheongju_only_rows.csv")
    cheongju_summary_path = os.path.join("data", "reports", "cheongju_only_summary.csv")

    cheongju_rows.to_csv(cheongju_only_path, index=False, encoding="utf-8-sig")
    cheongju_summary.to_csv(cheongju_summary_path, index=False, encoding="utf-8-sig")

    print(f"[INFO] 청주시 행 데이터 저장 → {cheongju_only_path}")
    print(f"[INFO] 청주시 지표 요약 저장 → {cheongju_summary_path}")

    # =========================
    # [5/5] 시각화
    # =========================
    print("=== [5/5] 시각화 ===")
    plot_accidents_by_region()

    print("=== 파이프라인 전체 완료 ===")


if __name__ == "__main__":
    run_pipeline()
