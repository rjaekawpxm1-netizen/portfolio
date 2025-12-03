import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font
from pandas.errors import EmptyDataError

from rpa_order_pipeline.config import RAW_DATA_PATH, REPORT_OUTPUT_PATH


def _load_or_create_dummy_df():
    """CSV가 비어있으면 더미 데이터로 DataFrame 생성."""
    try:
        if not os.path.exists(RAW_DATA_PATH) or os.path.getsize(RAW_DATA_PATH) == 0:
            raise EmptyDataError("빈 파일 또는 파일 없음")

        df = pd.read_csv(RAW_DATA_PATH)
        if df.empty:
            raise EmptyDataError("데이터 없음")

        return df

    except (EmptyDataError, FileNotFoundError):
        print("[WARN] 주문 데이터가 없어 더미 데이터를 생성합니다.")

        dummy = {
            "date": ["2025-12-01", "2025-12-01", "2025-12-02", "2025-12-02"],
            "order_id": ["O001", "O002", "O003", "O004"],
            "product": ["운동화", "티셔츠", "운동화", "바지"],
            "quantity": [1, 2, 1, 3],
            "price": [89000, 59000, 89000, 45000],
        }
        df = pd.DataFrame(dummy)
        # 참고용으로 CSV도 같이 저장해둠
        os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
        df.to_csv(RAW_DATA_PATH, index=False, encoding="utf-8-sig")

        return df


def build_report():
    print("[INFO] 주문 데이터 불러오는 중...")

    # ✅ 실제 크롤링 데이터 or 더미 데이터 로드
    df = _load_or_create_dummy_df()

    print("[INFO] 리포트 생성 시작...")

    # 숫자형 변환
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
    df["amount"] = df["quantity"] * df["price"]

    # ---- 📌 1. 기본 통계 ----
    total_orders = len(df)
    total_quantity = df["quantity"].sum()
    total_sales = df["amount"].sum()

    # ---- 📌 2. 제품별 판매량 ----
    product_summary = (
        df.groupby("product")
        .agg(total_quantity=("quantity", "sum"), total_sales=("amount", "sum"))
        .reset_index()
        .sort_values("total_sales", ascending=False)
    )

    # ---- 📌 3. Excel 리포트 생성 ----
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Summary"

    ws1["A1"] = "📌 주문 요약 리포트"
    ws1["A1"].font = Font(size=14, bold=True)

    ws1["A3"] = "총 주문 수"
    ws1["B3"] = total_orders

    ws1["A4"] = "총 판매 수량"
    ws1["B4"] = total_quantity

    ws1["A5"] = "총 매출액"
    ws1["B5"] = int(total_sales)

    # ---- 📌 Sheet2: 제품별 판매 요약 ----
    ws2 = wb.create_sheet("Product Summary")
    ws2.append(["제품명", "총 판매 수량", "총 매출"])

    for row in product_summary.itertuples(index=False):
        ws2.append([row.product, int(row.total_quantity), int(row.total_sales)])

    os.makedirs(os.path.dirname(REPORT_OUTPUT_PATH), exist_ok=True)
    wb.save(REPORT_OUTPUT_PATH)

    print("[INFO] 리포트 생성 완료 →", REPORT_OUTPUT_PATH)

    return REPORT_OUTPUT_PATH
