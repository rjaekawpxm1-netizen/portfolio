import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

########################################
# 1. 셀레니움 드라이버 실행
########################################
def start_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")  # 브라우저 안 보이게 하려면 주석 제거
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
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
    driver.get(url)
    time.sleep(2)

    print(f"📌 기사 접속 완료: {url}")

    # 댓글 영역까지 스크롤
    scroll_to_bottom(driver)

    # 페이지 HTML 가져오기
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    comment_blocks = soup.select(".u_cbox_text_wrap")
    print(f"🔍 수집된 댓글 블록 수: {len(comment_blocks)}")

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
if __name__ == "__main__":
    TEST_URLS = [
        "https://n.news.naver.com/mnews/article/449/0000328367",
        "https://n.news.naver.com/mnews/article/277/0005688485",
        "https://n.news.naver.com/mnews/article/214/0001465786"
    ]

    all_comments = []

    for url in TEST_URLS:
        print("\n=====================================")
        print(f"🚀 댓글 수집 시작: {url}")
        print("=====================================")

        df = get_comments_from_url(url)
        print(f"➡ 수집된 댓글 수: {len(df)}")

        df["article_url"] = url
        all_comments.append(df)

    final_df = pd.concat(all_comments, ignore_index=True)
    final_df.to_csv("../data/raw/comments_selenium.csv", index=False, encoding="utf-8-sig")

    print("\n🎉 완료! 저장된 파일:")
    print("../data/raw/comments_selenium.csv")
