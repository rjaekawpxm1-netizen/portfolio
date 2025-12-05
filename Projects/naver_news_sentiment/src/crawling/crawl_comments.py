import requests
import json
import pandas as pd
import time
import os
from urllib.parse import urlparse


def extract_oid_aid(url: str):
    path = urlparse(url).path
    parts = path.split("/")
    oid = parts[-2]
    aid = parts[-1]
    return oid, aid

def get_comments_from_article(url, max_pages=30):
    oid, aid = extract_oid_aid(url)

    all_comments = []

    for page in range(1, max_pages + 1):
        api_url = (
            "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json"
            f"?ticket=news&templateId=default&pool=cbox5&lang=ko&country=KR"
            f"&objectId=news{oid},{aid}&pageSize=20&page={page}"
        )

        res = requests.get(api_url, headers={"User-Agent": "Mozilla/5.0"})
        print(f"[DEBUG] status_code={res.status_code}, page={page}")  # ★ 추가

        if res.status_code != 200:
            print("요청 실패:", res.status_code)
            break

        text = res.text
        start = text.find("(") + 1
        end = text.rfind(")")
        json_str = text[start:end]

        data = json.loads(json_str)
        print("[DEBUG JSON]", json_str[:500])


        # ★ 페이지 1에서 총 댓글 수 출력
        if page == 1:
            total_count = data.get("result", {}).get("count", {}).get("comment", "알 수 없음")
            print(f"[DEBUG] 이 기사 총 댓글 수: {total_count}")

        comment_list = data.get("result", {}).get("commentList", [])
        if not comment_list:
            # 더 이상 댓글이 없으면 종료
            break

        for c in comment_list:
            all_comments.append({
                "contents": c.get("contents"),
                "like": c.get("sympathyCount"),
                "dislike": c.get("antipathyCount"),
                "reply_count": c.get("replyCount"),
                "user_id": c.get("userIdNo"),
                "mod_time": c.get("modTime"),
                "reg_time": c.get("regTime"),
            })

        time.sleep(0.3)

    return pd.DataFrame(all_comments)



if __name__ == "__main__":
    os.makedirs("../data/raw", exist_ok=True)

    # 1) 아까 저장한 뉴스 리스트 불러오기
    news_df = pd.read_csv("../data/raw/manual_news.csv")

    all_result = []

    for idx, row in news_df.iterrows():
        print(f"[{idx+1}/{len(news_df)}] 기사 크롤링 중...")
        url = row["url"]
        section_id = row["section_id"]
        title = row["title"]

        try:
            df_comments = get_comments_from_article(url, max_pages=30)
            if df_comments.empty:
                continue

            df_comments["section_id"] = section_id
            df_comments["article_title"] = title
            df_comments["article_url"] = url

            all_result.append(df_comments)
        except Exception as e:
            print("에러 발생:", e)
            continue

    if all_result:
        final_df = pd.concat(all_result, ignore_index=True)
        final_df.to_csv("../data/raw/comments.csv", index=False, encoding="utf-8-sig")
        print("저장 완료: ../data/raw/comments.csv")
    else:
        print("수집된 댓글이 없습니다.")
