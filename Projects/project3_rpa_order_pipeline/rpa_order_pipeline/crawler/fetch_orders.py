from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

from rpa_order_pipeline.config import ORDER_URL, RAW_DATA_PATH


def fetch_order_data():
    print("[INFO] 웹 주문 데이터 크롤링 시작...")

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(ORDER_URL)
    
    time.sleep(2)

    rows = driver.find_elements(By.CSS_SELECTOR, "table tr")

    data = []
    for row in rows[1:]:
        cols = row.find_elements(By.TAG_NAME, "td")
        data.append({
            "date": cols[0].text,
            "order_id": cols[1].text,
            "product": cols[2].text,
            "quantity": cols[3].text,
            "price": cols[4].text,
        })

    df = pd.DataFrame(data)
    df.to_csv(RAW_DATA_PATH, index=False, encoding="utf-8-sig")

    driver.quit()
    print("[INFO] 크롤링 완료 →", RAW_DATA_PATH)

    return df
