import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INPUT_PATH = "./data/processed/comments_with_sentiment.csv"
OUTPUT_PATH = "./data/processed/article_reports.csv"

# ============================
# 1. 데이터 로드
# ============================
def load_data():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"{INPUT_PATH} 파일을 찾을 수 없습니다.")

    df = pd.read_csv(INPUT_PATH)

    # 컬럼 이름 정규화
    cols = {c.lower(): c for c in df.columns}
    comment_col = cols.get("comment", None)
    clean_col = cols.get("comment_clean", None)
    senti_col = cols.get("sentiment", None)
    url_col = cols.get("article_url", None)

    if url_col is None:
        raise ValueError("article_url 컬럼이 필요합니다. (기사별 그룹핑에 사용)")

    if clean_col:
        df["text_for_analysis"] = df[clean_col].fillna("")
    elif comment_col:
        df["text_for_analysis"] = df[comment_col].fillna("")
    else:
        raise ValueError("comment / comment_clean 컬럼을 찾을 수 없습니다.")

    if senti_col is None:
        df["sentiment"] = "중립"

    return df, url_col


# ============================
# 2. 기사별 리포트 생성
# ============================
def build_prompt(article_url, sub_df):
    total = len(sub_df)
    senti_counts = sub_df["sentiment"].value_counts().to_dict()

    # 예시 댓글 몇 개만 사용 (너무 많으면 프롬프트 길어짐)
    examples = []
    for i, row in sub_df.head(15).iterrows():
        examples.append(f"- ({row['sentiment']}) {row['text_for_analysis']}")
    examples_str = "\n".join(examples)

    prompt = f"""
너는 뉴스 기사에 달린 댓글을 분석하는 데이터 분석가야.

아래는 특정 기사에 대한 댓글 데이터다.

[기사 URL]
{article_url}

[전체 댓글 수]
{total}개

[감정 분포]
{', '.join([f"{k}: {v}개" for k, v in senti_counts.items()])}

[댓글 예시]
{examples_str}

위 정보를 바탕으로, 한국어로 다음 항목을 포함한 간단한 리포트를 작성해줘.

1. 전체 댓글 분위기 요약 (2~3문장)
2. 긍정적인 반응이 있다면 어떤 내용인지
3. 부정적인 반응이 있다면 어떤 내용인지
4. 중립/정보 전달형 댓글이 있다면 특징
5. 한 문장으로 정리한 결론

항목 번호를 유지해서 깔끔하게 bullet 형식으로 작성해줘.
"""
    return prompt


def generate_report(article_url, sub_df):
    prompt = build_prompt(article_url, sub_df)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return completion.choices[0].message.content


# ============================
# 3. 메인 실행
# ============================
if __name__ == "__main__":
    df, url_col = load_data()

    reports = []

    # 기사 URL별 그룹핑
    grouped = df.groupby(url_col)

    # 너무 많으면 상위 N개만 할 수도 있음
    MAX_ARTICLES = 10  # 필요하면 조정
    for idx, (article_url, sub_df) in enumerate(grouped):
        if idx >= MAX_ARTICLES:
            break

        print(f"\n📰 [{idx+1}] 기사 리포트 생성 중: {article_url}")
        try:
            report_text = generate_report(article_url, sub_df)
        except Exception as e:
            print("⚠️ 오류 발생:", e)
            report_text = "생성 실패"

        reports.append({
            "article_url": article_url,
            "comment_count": len(sub_df),
            "report": report_text
        })

    out_df = pd.DataFrame(reports)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    out_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("\n🎉 기사별 리포트 생성 완료!")
    print("저장 위치:", OUTPUT_PATH)
