import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_path, description):
    print("\n===================================")
    print(f"🚀 실행 중: {description}")
    print(f"▶ 스크립트: {script_path}")
    print("===================================\n")

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True
    )

    # 표준 출력
    if result.stdout:
        print(result.stdout)

    # 오류 출력
    if result.stderr:
        print("⚠️ stderr 출력:")
        print(result.stderr)

    # 종료 코드 체크
    if result.returncode != 0:
        print(f"❌ {description} 단계에서 오류 발생 (returncode={result.returncode})")
        # 필요하면 여기서 바로 종료
        sys.exit(result.returncode)

if __name__ == "__main__":

    # 1단계: 뉴스 URL 자동 수집
    crawl_news_urls = os.path.join(BASE_DIR, "crawl_news_urls.py")
    run_script(crawl_news_urls, "1단계 - 뉴스 URL 수집")

    # 2단계: Selenium 댓글 수집
    crawl_comments = os.path.join(BASE_DIR, "naver_comment_selenium.py")
    run_script(crawl_comments, "2단계 - 댓글 수집")

    # 🔜 3단계: 감정 분석
    sentiment_analysis = os.path.join(BASE_DIR, "sentiment_analysis.py")
    if os.path.exists(sentiment_analysis):
        run_script(sentiment_analysis, "3단계 - 감정 분석")

    # 🔜 4단계: 텍스트/악성댓글 분석 (있으면)
    text_analysis = os.path.join(BASE_DIR, "text_analysis.py")
    if os.path.exists(text_analysis):
        run_script(text_analysis, "4단계 - 텍스트/악성 댓글 분석")

    # 🔜 5단계: 시각화
    visualize = os.path.join(BASE_DIR, "visualize_sentiment.py")
    if os.path.exists(visualize):
        run_script(visualize, "5단계 - 시각화 생성")

    print("\n===================================")
    print("🎉 전체 파이프라인 완료!")
    print("👉 data/raw, data/processed, data/figures 폴더를 확인하세요.")
    print("===================================\n")
