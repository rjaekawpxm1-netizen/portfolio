import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(rel_path, description):
    script_path = os.path.join(BASE_DIR, *rel_path.split("/"))

    print("\n===================================")
    print(f"🚀 실행 중: {description}")
    print(f"▶ 스크립트: {script_path}")
    print("===================================\n")

    if not os.path.exists(script_path):
        print(f"❌ {description} : 스크립트를 찾을 수 없습니다.")
        print(f"   경로를 다시 확인하세요 → {script_path}")
        sys.exit(1)

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print("⚠️ stderr 출력:")
        print(result.stderr)

    if result.returncode != 0:
        print(f"❌ {description} 단계에서 오류 발생 (returncode={result.returncode})")
        sys.exit(result.returncode)

if __name__ == "__main__":
    # 1단계: 뉴스 URL 수집
    run_script("crawling/crawl_news_urls.py", "1단계 - 뉴스 URL 수집")

    # 2단계: 댓글 수집 (Selenium)
    run_script("crawling/naver_comment_selenium.py", "2단계 - 댓글 수집")

    # 3단계: 감정 분석
    run_script("analysis/sentiment_analysis.py", "3단계 - 감정 분석")

    # 4단계: 텍스트/악성 댓글 분석 (있으면)
    if os.path.exists(os.path.join(BASE_DIR, "analysis", "text_analysis.py")):
        run_script("analysis/text_analysis.py", "4단계 - 텍스트/악성 댓글 분석")

    # 4-1단계(v2): 기사/섹션 단위 요약 생성
    if os.path.exists(os.path.join(BASE_DIR, "analysis", "article_level_analysis.py")):
        run_script("analysis/article_level_analysis.py", "4-1단계(v2) - 기사/섹션 단위 요약")

    # 5단계: 시각화 (있으면)
    if os.path.exists(os.path.join(BASE_DIR, "analysis", "visualize_sentiment.py")):
        run_script("analysis/visualize_sentiment.py", "5단계 - 시각화 생성")

    print("\n===================================")
    print("🎉 전체 파이프라인 완료!")
    print("👉 data/raw, data/processed, data/figures 폴더를 확인하세요.")
    print("===================================\n")
