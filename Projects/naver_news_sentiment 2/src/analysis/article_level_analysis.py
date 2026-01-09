import os
import pandas as pd

"""Article-level aggregation for v2.

This script upgrades the project from "overall sentiment" to "article/section-level" insights.

Outputs (created under data/processed):
  1) article_sentiment_summary.csv
  2) section_sentiment_summary.csv

Expected inputs:
  - data/processed/comments_with_sentiment_hate.csv
  - data/raw/news_urls.csv
"""


BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # .../src/analysis
SRC_DIR = os.path.dirname(BASE_DIR)                       # .../src
ROOT_DIR = os.path.dirname(SRC_DIR)                       # project root

RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")


def _to_int_series(s: pd.Series) -> pd.Series:
    """Robust numeric conversion for like/dislike columns."""
    return (
        s.astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace({"": "0", "nan": "0", "None": "0"})
        .astype(float)
        .fillna(0)
        .astype(int)
    )


def load_inputs(
    comments_name: str = "comments_with_sentiment_hate.csv",
    urls_name: str = "news_urls.csv",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    comments_path = os.path.join(PROCESSED_DIR, comments_name)
    urls_path = os.path.join(RAW_DIR, urls_name)

    if not os.path.exists(comments_path):
        raise FileNotFoundError(
            f"{comments_path} 파일을 찾을 수 없습니다. 먼저 sentiment_analysis.py → text_analysis.py 순서로 실행하세요."
        )
    if not os.path.exists(urls_path):
        raise FileNotFoundError(
            f"{urls_path} 파일을 찾을 수 없습니다. 먼저 crawling/crawl_news_urls.py 를 실행하세요."
        )

    comments = pd.read_csv(comments_path)
    urls = pd.read_csv(urls_path)

    # 최소 컬럼 체크
    required = {"comment", "article_url", "sentiment"}
    missing = sorted(list(required - set(comments.columns)))
    if missing:
        raise KeyError(f"댓글 데이터에 필요한 컬럼이 없습니다: {missing}")

    # like/dislike, is_hate 컬럼은 없을 수도 있으니 없으면 기본값으로 채워줌
    if "like" not in comments.columns:
        comments["like"] = 0
    if "dislike" not in comments.columns:
        comments["dislike"] = 0
    if "is_hate" not in comments.columns:
        comments["is_hate"] = 0

    comments["like"] = _to_int_series(comments["like"])
    comments["dislike"] = _to_int_series(comments["dislike"])
    comments["is_hate"] = _to_int_series(comments["is_hate"])

    # urls 최소 컬럼
    if "url" not in urls.columns:
        raise KeyError("news_urls.csv 에 'url' 컬럼이 없습니다.")
    if "section" not in urls.columns:
        urls["section"] = "미분류"

    return comments, urls


def make_article_summary(comments: pd.DataFrame, urls: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to article-level metrics."""
    url_map = urls[["url", "section"]].drop_duplicates("url")
    merged = comments.merge(url_map, left_on="article_url", right_on="url", how="left")
    merged["section"] = merged["section"].fillna("미분류")

    # v2용: 댓글 데이터에 섹션을 붙여 저장하기 위해 반환
    merged_comments = merged.drop(columns=["url"], errors="ignore")

    # sentiment count pivot
    pivot = (
        merged.pivot_table(
            index=["article_url", "section"],
            columns="sentiment",
            values="comment",
            aggfunc="count",
            fill_value=0,
        )
        .reset_index()
    )

    for col in ["긍정", "중립", "부정"]:
        if col not in pivot.columns:
            pivot[col] = 0

    pivot = pivot.rename(columns={"긍정": "pos_cnt", "중립": "neu_cnt", "부정": "neg_cnt"})
    pivot["n_comments"] = pivot[["pos_cnt", "neu_cnt", "neg_cnt"]].sum(axis=1)

    # like/dislike/hate aggregations
    agg = (
        merged.groupby(["article_url", "section"], as_index=False)
        .agg(
            avg_like=("like", "mean"),
            avg_dislike=("dislike", "mean"),
            net_like=("like", "sum"),
            net_dislike=("dislike", "sum"),
            hate_ratio=("is_hate", "mean"),
        )
    )

    out = pivot.merge(agg, on=["article_url", "section"], how="left")

    # ratios
    out["pos_ratio"] = (out["pos_cnt"] / out["n_comments"]).fillna(0)
    out["neu_ratio"] = (out["neu_cnt"] / out["n_comments"]).fillna(0)
    out["neg_ratio"] = (out["neg_cnt"] / out["n_comments"]).fillna(0)

    # interpretable scores
    # sentiment_score: -1~+1  (pos - neg) / total
    out["sentiment_score"] = ((out["pos_cnt"] - out["neg_cnt"]) / out["n_comments"]).fillna(0)
    # risk_score: 0~100-ish  (neg ratio + hate ratio + (dislike pressure))
    # - neg_ratio(0~1) * 60
    # - hate_ratio(0~1) * 25
    # - dislike dominance (net_dislike / (net_like + net_dislike + 1)) * 15
    dislike_pressure = out["net_dislike"] / (out["net_like"] + out["net_dislike"] + 1)
    out["risk_score"] = (
        out["neg_ratio"] * 60
        + out["hate_ratio"] * 25
        + dislike_pressure * 15
    )

    # risk level by percentiles (Top 20% = HIGH, next 30% = MEDIUM)
    if len(out) >= 5:
        q80 = out["risk_score"].quantile(0.8)
        q50 = out["risk_score"].quantile(0.5)
        out["risk_level"] = out["risk_score"].apply(
            lambda x: "HIGH" if x >= q80 else ("MEDIUM" if x >= q50 else "LOW")
        )
    else:
        out["risk_level"] = "LOW"

    # 정렬: 리스크 높은 기사 먼저
    out = out.sort_values(["risk_score", "n_comments"], ascending=[False, False]).reset_index(drop=True)
    return out, merged_comments


def make_section_summary(article_summary: pd.DataFrame) -> pd.DataFrame:
    """Aggregate article summary to section-level."""
    sec = (
        article_summary.groupby("section", as_index=False)
        .agg(
            n_articles=("article_url", "count"),
            n_comments=("n_comments", "sum"),
            pos_ratio=("pos_ratio", "mean"),
            neu_ratio=("neu_ratio", "mean"),
            neg_ratio=("neg_ratio", "mean"),
            hate_ratio=("hate_ratio", "mean"),
            sentiment_score=("sentiment_score", "mean"),
            risk_score=("risk_score", "mean"),
        )
        .sort_values("risk_score", ascending=False)
        .reset_index(drop=True)
    )
    return sec


def main():
    comments, urls = load_inputs()
    print(f"📂 입력 로드 완료: comments={len(comments):,}, urls={len(urls):,}")

    article_summary, comments_enriched = make_article_summary(comments, urls)
    section_summary = make_section_summary(article_summary)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    out1 = os.path.join(PROCESSED_DIR, "article_sentiment_summary.csv")
    out2 = os.path.join(PROCESSED_DIR, "section_sentiment_summary.csv")
    out3 = os.path.join(PROCESSED_DIR, "comments_with_section.csv")
    article_summary.to_csv(out1, index=False, encoding="utf-8-sig")
    section_summary.to_csv(out2, index=False, encoding="utf-8-sig")
    comments_enriched.to_csv(out3, index=False, encoding="utf-8-sig")

    print("✅ v2 기사/섹션 단위 요약 생성 완료!")
    print(f"- 기사 요약: {out1}")
    print(f"- 섹션 요약: {out2}")
    print(f"- 댓글(섹션 포함): {out3}")


if __name__ == "__main__":
    main()
