import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from pathlib import Path


########################################
# 1. 셀레니움 드라이버 실행
########################################
def start_driver(headless=False):
    print("[DEBUG] Selenium 크롤러 시작됨")
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # headless=True 로 호출하면 브라우저 창 안 보이게 실행
    if headless:
        # 최신 크롬에서는 --headless=new 권장
        options.add_argument("--headless=new")

    print("[DEBUG] Chrome driver 생성 시도중...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    print("[DEBUG] Chrome driver 생성 완료")
    return driver


########################################
# 2. 댓글 모두 펼치기 (스크롤 끝까지)
########################################
def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(1.5)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


########################################
# 3. 댓글 수집 함수
########################################
def get_comments_from_url(url):
    driver = start_driver()
    print(f"[DEBUG] 기사 페이지 접근: {url}")
    driver.get(url)
    print("[DEBUG] 페이지 로딩 완료")

    time.sleep(2)

    print(f"[INFO] 기사 접속 완료: {url}")

    # 댓글 영역까지 스크롤
    scroll_to_bottom(driver)

    # 페이지 HTML 가져오기
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    comment_blocks = soup.select(".u_cbox_text_wrap")
    print(f"[INFO] 수집된 댓글 블록 수: {len(comment_blocks)}")

    comments = []
    for block in comment_blocks:
        try:
            comment = block.select_one(".u_cbox_contents").get_text(strip=True)
        except:
            comment = ""

        try:
            date = block.select_one(".u_cbox_date").get_text(strip=True)
        except:
            date = ""

        try:
            like = block.select_one(".u_cbox_cnt_recomm").get_text(strip=True)
        except:
            like = "0"

        try:
            dislike = block.select_one(".u_cbox_cnt_unrecomm").get_text(strip=True)
        except:
            dislike = "0"

        comments.append({
            "comment": comment,
            "date": date,
            "like": like,
            "dislike": dislike
        })

    driver.quit()
    return pd.DataFrame(comments)


########################################
# 4. 메인 실행
########################################
import pandas as pd

if __name__ == "__main__":

    # 자동으로 URL 읽기
    BASE_DIR = Path(__file__).resolve().parents[2]  # 프로젝트 루트
    raw_dir = BASE_DIR / "data" / "raw"

    news_url_path = raw_dir / "news_urls.csv"
    if not news_url_path.exists():
        raise FileNotFoundError(f"❌ news_urls.csv 없음: {news_url_path}")

    df_urls = pd.read_csv(news_url_path, encoding="utf-8-sig")
    print(f"✅ URL 로드 완료: {len(df_urls)}건")

    TEST_URLS = df_urls["url"].tolist()

    all_comments = []

    for url in TEST_URLS:
        print("\n=====================================")
        print(f"[START] 댓글 수집 시작: {url}")
        print("=====================================")

        df = get_comments_from_url(url)
        print(f"[INFO] 수집된 댓글 수: {len(df)}")

        if len(df) > 0:
            df["article_url"] = url
            all_comments.append(df)

    from pathlib import Path

# 프로젝트 루트 기준 경로 설정
BASE_DIR = Path(__file__).resolve().parents[2]
raw_dir = BASE_DIR / "data" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)

# 빈 리스트 예외 처리
if len(all_comments) > 0:
    final_df = pd.concat(all_comments, ignore_index=True)

    out_path = raw_dir / "comments_selenium.csv"
    final_df.to_csv(out_path, index=False, encoding="utf-8-sig")

    print("\n[DONE] 완료! 저장된 파일:")
    print(out_path)
else:
    print("⚠️ 수집된 댓글이 없습니다. 뉴스 URL이 있는지 확인하세요.")
