import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font

from rpa_order_pipeline.config import RAW_DATA_PATH, REPORT_OUTPUT_PATH


def build_report():
    print("[INFO] 주문 데이터 불러오는 중...")

    # 크롤링해서 저장한 CSV 로드
    df = pd.read_csv(RAW_DATA_PATH)

    print("[INFO] 리포트 생성 시작...")

    # ---- 📌 1. 기본 통계 ----
    total_orders = len(df)
    total_quantity = df["quantity"].astype(int).sum()
    total_sales = df["price"].astype(int).sum()

    # ---- 📌 2. 제품별 판매량 ----
    product_summary = (
        df.groupby("product")
        .agg(total_quantity=("quantity", "sum"), total_sales=("price", "sum"))
        .reset_index()
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
    ws1["B5"] = total_sales

    # ---- 📌 Sheet2: 제품별 판매 요약 ----
    ws2 = wb.create_sheet("Product Summary")

    ws2.append(["제품명", "총 판매 수량", "총 매출"])
    for row in product_summary.itertuples(index=False):
        ws2.append(list(row))

    # 저장
    wb.save(REPORT_OUTPUT_PATH)

    print("[INFO] 리포트 생성 완료 →", REPORT_OUTPUT_PATH)

    return REPORT_OUTPUT_PATH
