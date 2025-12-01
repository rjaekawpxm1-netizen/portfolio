import requests
from rpa_order_pipeline.config import SLACK_WEBHOOK_URL, REPORT_OUTPUT_PATH


def send_slack_notification():
    if not SLACK_WEBHOOK_URL:
        print("[WARN] SLACK_WEBHOOK_URL 이 설정되지 않아 슬랙 알림을 건너뜁니다.")
        return

    text = (
        ":bar_chart: *주문 리포트 생성 완료*\n"
        f"리포트 파일 위치: `{REPORT_OUTPUT_PATH}`\n"
        "_(자동 발송 메시지)_"
    )

    payload = {"text": text}
    resp = requests.post(SLACK_WEBHOOK_URL, json=payload)

    if resp.status_code == 200:
        print("[INFO] Slack 알림 전송 완료")
    else:
        print("[ERROR] Slack 전송 실패:", resp.status_code, resp.text)
