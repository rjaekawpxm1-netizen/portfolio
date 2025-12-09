# cheongju/main.py
import os

from cheongju.api.fetch_accident_data import fetch_accident_data
from cheongju.preprocessing.clean_data import clean_accident_data
from cheongju.analysis.basic_stats import summarize_korea_and_cheongju
from cheongju.viz.make_plots import plot_accidents_by_region


def ensure_dirs() -> None:
    """프로젝트에서 사용하는 기본 디렉토리들을 생성한다."""
    base_dirs = [
        os.path.join("data", "raw"),
        os.path.join("data", "processed"),
        os.path.join("data", "reports"),
    ]
    for d in base_dirs:
        os.makedirs(d, exist_ok=True)


def run_pipeline() -> None:
    ensure_dirs()

    # 1. 교통사고 데이터 수집
    print("=== [1/4] 교통사고 데이터 수집 ===")
    df_raw = fetch_accident_data()

    raw_path = os.path.join("data", "raw", "accidents_raw.csv")
    df_raw.to_csv(raw_path, index=False, encoding="utf-8-sig")
    print(f"[INFO] 저장 완료 → {raw_path}")

    # 2. 전처리
    print("=== [2/4] 데이터 전처리 ===")
    df_clean = clean_accident_data()

    processed_path = os.path.join("data", "processed", "accidents_clean.csv")
    df_clean.to_csv(processed_path, index=False, encoding="utf-8-sig")
    print(f"[INFO] 전처리 완료 → {processed_path}")

    # 3. 기초 통계 분석
    print("=== [3/4] 기초 통계 분석 ===")
    df_summary, cheongju_df, cheongju_rank = summarize_korea_and_cheongju()

    reports_dir = os.path.join("data", "reports")
    os.makedirs(reports_dir, exist_ok=True)

    summary_path = os.path.join(reports_dir, "accidents_summary_by_region.csv")
    df_summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    cheongju_path = os.path.join(reports_dir, "cheongju_accident_summary.csv")
    cheongju_df.to_csv(cheongju_path, index=False, encoding="utf-8-sig")

    print(f"[INFO] 전국 요약 저장 → {summary_path}")
    print(f"[INFO] 청주시 요약 저장 → {cheongju_path}")
    print(f"[INFO] 청주시 사상자 순위: {cheongju_rank}위")

    # 4. 시각화 (함수 내부에서 processed 데이터 불러온다고 가정)
    print("=== [4/4] 시각화 생성 ===")
    plot_accidents_by_region()
    print("[INFO] 시각화 생성 완료")

    print("=== 파이프라인 완료 ===")


if __name__ == "__main__":
    run_pipeline()
