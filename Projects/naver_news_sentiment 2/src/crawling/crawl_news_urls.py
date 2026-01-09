import requests
from bs4 import BeautifulSoup
import pandas as pd

SECTIONS = {
    "사회": "https://news.naver.com/section/102",
    "연예": "https://news.naver.com/section/106",
    "스포츠": "https://news.naver.com/section/105",
}

def get_article_urls(section_name, url):
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")

    articles = soup.select("a.sa_text_title")  # 네이버 뉴스 제목 링크 (정확함)

    urls = []
    for a in articles:
        href = a.get("href")
        if href.startswith("https://n.news.naver.com/"):
            urls.append(href)

    print(f"[{section_name}] 수집된 기사 수: {len(urls)}")
    return urls


if __name__ == "__main__":
    all_urls = []

    for name, url in SECTIONS.items():
        urls = get_article_urls(name, url)
        for u in urls:
            all_urls.append({"section": name, "url": u})

    df = pd.DataFrame(all_urls)
    df.to_csv("../data/raw/news_urls.csv", index=False, encoding="utf-8-sig")

    print("완료! ./data/raw/news_urls.csv 로 저장됨")
