import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# 네이버 뉴스 섹션 URL (정치, 사회, 연예)
SECTION_URLS = {
    "100": "https://news.naver.com/section/100",  # 정치
    "102": "https://news.naver.com/section/102",  # 사회
    "106": "https://news.naver.com/section/106",  # 연예
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


def get_news_list(section_id: str, limit: int = 30) -> pd.DataFrame:
    """
    네이버 뉴스 섹션 페이지에서
    'https://n.news.naver.com/mnews/article/...' 형태의 기사 링크만 골라서 수집
    """
    url = SECTION_URLS[section_id]
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    links = []
    titles = []

    # a 태그 중에서 기사 링크 패턴만 필터링
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # 모바일 기사 패턴만 사용
        if "https://n.news.naver.com/mnews/article/" in href:
            title = a.get_text(strip=True)
            if not title:
                continue

            # 중복 제거
            if href in links:
                continue

            links.append(href)
            titles.append(title)

        if len(links) >= limit:
            break

    df = pd.DataFrame({
        "section_id": section_id,
        "title": titles,
        "url": links,
    })
    return df


if __name__ == "__main__":
    os.makedirs("../data/raw", exist_ok=True)

    all_df = []

    for sec in ["100", "102", "106"]:
        print(f"[{sec}] 섹션 수집 중...")
        df = get_news_list(sec, limit=20)
        print(f"  → {len(df)}개 기사 수집")
        all_df.append(df)

    result = pd.concat(all_df, ignore_index=True)
    result.to_csv("../data/raw/news_list.csv", index=False, encoding="utf-8-sig")

    print("저장 완료: ../data/raw/news_list.csv")
