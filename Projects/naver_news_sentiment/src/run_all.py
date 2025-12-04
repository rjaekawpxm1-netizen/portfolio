import os
import subprocess

def run_script(script_name):
    print("\n===================================")
    print(f"🚀 실행 중: {script_name}")
    print("===================================\n")

    result = subprocess.run(
        ["python", script_name], 
        capture_output=True, 
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print("⚠️ 오류 발생:")
        print(result.stderr)


if __name__ == "__main__":

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 1단계: 뉴스 URL 자동 수집
    crawl_news_urls = os.path.join(BASE_DIR, "crawl_news_urls.py")
    run_script(crawl_news_urls)

    # 2단계: Selenium 댓글 수집
    crawl_comments = os.path.join(BASE_DIR, "naver_comment_selenium.py")
    run_script(crawl_comments)

    print("\n===================================")
    print("🎉 전체 크롤링 완료! 모든 작업이 끝났습니다!")
    print("👉 news_urls.csv & comments_selenium.csv 확인하세요.")
    print("===================================\n")
