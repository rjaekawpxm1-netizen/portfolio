# cheongju/analysis/basic_stats.py

import os
import pandas as pd


def load_clean_data() -> pd.DataFrame:
    """
    전처리된 교통사고 데이터를 불러오는 함수.
    """
    path = os.path.join("data", "processed", "accidents_clean.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"전처리된 파일을 찾을 수 없습니다: {path}")

    df = pd.read_csv(path)
    return df


def summarize_korea_and_cheongju():
    """
    - 전국 시군구별 사상자 수 합계 계산
    - 청주시 데이터만 따로 추출
    - 청주시의 전국 순위 계산
    """
    df = load_clean_data()

    # 사상자(사망 + 중상 + 경상 + 부상신고) 합계 컬럼 추가
    df["사상자수_합계"] = (
        df[["사망자수", "중상자수", "경상자수", "부상신고자수"]]
        .sum(axis=1)
    )

    # 전국 기준으로 사상자수 내림차순 정렬
    df_sorted = df.sort_values("사상자수_합계", ascending=False).reset_index(drop=True)

    # 청주시만 필터링 (시도=충북, 시군구=청주시)
    cheongju_df = df_sorted[
        (df_sorted["시도"] == "충북") & (df_sorted["시군구"] == "청주시")
    ].copy()

    if cheongju_df.empty:
        print("[WARN] 청주시 데이터가 없습니다. 필터 조건을 다시 확인하세요.")
        cheongju_rank = None
    else:
        # 청주시 순위 (0부터 시작하니 +1)
        cheongju_rank = (
            df_sorted.index[df_sorted["시도"].eq("충북") & df_sorted["시군구"].eq("청주시")][0]
            + 1
        )

    print("=== [3/5] 기초 통계 분석 결과 ===")
    print(f"[INFO] 전체 시군구 개수: {len(df_sorted)}")
    if not cheongju_df.empty:
        row = cheongju_df.iloc[0]
        print(
            f"[INFO] 청주시 사고건수: {row['사고건수']}, "
            f"사상자수 합계: {row['사상자수_합계']}, "
            f"전국 사상자수 순위: {cheongju_rank}위"
        )

    return df_sorted, cheongju_df, cheongju_rank
