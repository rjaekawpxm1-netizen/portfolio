import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 웹사이트 URL (예: 주문 조회 페이지)
ORDER_URL = os.getenv("ORDER_URL")

# 크롬 드라이버 경로
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")

# Slack Webhook URL
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# 데이터 경로
RAW_DATA_PATH = "data/raw/orders.csv"
REPORT_OUTPUT_PATH = "data/reports/report.xlsx"
