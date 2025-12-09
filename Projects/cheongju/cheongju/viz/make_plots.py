import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_accidents_by_region():

    input_path = os.path.join("data", "processed", "accidents_clean.csv")
    df = pd.read_csv(input_path)

    # 시군구별 사고 총합
    region_summary = df.groupby("시군구")[["사고건수", "사망자수", "부상신고자수"]].sum()

    plt.figure(figsize=(12, 6))
    region_summary["사고건수"].sort_values(ascending=False).plot(kind="bar")

    plt.title("시군구별 교통사고 건수")
    plt.xlabel("시군구")
    plt.ylabel("사고 건수")
    plt.tight_layout()

    output_path = os.path.join("data", "reports", "accidents_by_region.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.savefig(output_path)
    print(f"[INFO] 그래프 저장 완료 → {output_path}")
    plt.close()
