import os
import pandas as pd

def analyze_cheongju_by_district(
    input_path: str = os.path.join("data", "processed", "lgstat_clean.csv"),
):
    df = pd.read_csv(input_path)

    # ✅ 충청북도 + 청주시 + '구' 있는 행만
    cheongju = df[(df["시도"] == "충청북도") & (df["시군구"] == "청주시")].copy()
    cheongju = cheongju[cheongju["구"].astype(str).str.endswith("구")].copy()

    if cheongju.empty:
        raise ValueError(
            "청주시 구 데이터가 비었습니다.\n"
            "sido_sgg_nm 샘플을 확인해서 '충청북도 청주시 흥덕구' 형태로 오는지 먼저 체크하세요."
        )

    out = (
        cheongju.groupby("구")[["acc_cnt", "dth_dnv_cnt", "injpsn_cnt"]]
        .sum()
        .reset_index()
        .rename(columns={
            "acc_cnt": "사고건수",
            "dth_dnv_cnt": "사망자수",
            "injpsn_cnt": "부상자수",
        })
    )
    out["사상자수"] = out["사망자수"] + out["부상자수"]
    out["사고 1건당 사상자수"] = (out["사상자수"] / out["사고건수"]).round(4)

    return out
