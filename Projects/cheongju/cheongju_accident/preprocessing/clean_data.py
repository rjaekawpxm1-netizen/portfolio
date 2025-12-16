import pandas as pd
import os

def clean_accident_data():
    print("[INFO] 데이터 전처리 시작")

    raw_path = os.path.join("data", "raw", "accidents_raw.csv")
    df = pd.read_csv(raw_path)

    print("[INFO] 원본 데이터 shape:", df.shape)

    # 🔥 현재 CSV 컬럼명 출력해보자
    print("[INFO] CSV 컬럼명:", df.columns.tolist())

    # 🔥 (임시) 청주시 필터링 제거
    # 나중에 다른 API 연결하면 다시 적용할 것
    df_filtered = df.copy()
    print("[INFO] 필터링 후 데이터 shape:", df_filtered.shape)

    # 🔥 존재하는 컬럼만 숫자 변환 처리
    numeric_cols = [col for col in df_filtered.columns if "사망" in col or "부상" in col or "인원" in col]
    print("[INFO] 숫자 변환 대상 컬럼:", numeric_cols)

    for col in numeric_cols:
        df_filtered[col] = pd.to_numeric(df_filtered[col], errors="coerce")

    # 🔥 존재하는 컬럼만 dropna 적용
    drop_cols = [col for col in ["사망자수", "부상자수"] if col in df_filtered.columns]
    if drop_cols:
        df_filtered = df_filtered.dropna(subset=drop_cols)

    # 저장
    processed_path = os.path.join("data", "processed", "accidents_clean.csv")
    df_filtered.to_csv(processed_path, index=False, encoding="utf-8-sig")

    print(f"[INFO] 전처리 완료 → {processed_path}")
    return df_filtered
