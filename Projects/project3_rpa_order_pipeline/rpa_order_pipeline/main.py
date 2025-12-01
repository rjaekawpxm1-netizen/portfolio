from rpa_order_pipeline.crawler.fetch_orders import fetch_order_data
from rpa_order_pipeline.processor.build_report import build_report
from rpa_order_pipeline.notifier.slack_notify import send_slack_notification


def run_pipeline():
    print("=== [1/3] 주문 데이터 크롤링 ===")
    fetch_order_data()

    print("=== [2/3] 리포트 생성 ===")
    report_path = build_report()

    print("=== [3/3] Slack 알림 전송 ===")
    send_slack_notification()

    print("=== 파이프라인 완료 ===")


if __name__ == "__main__":
    run_pipeline()
