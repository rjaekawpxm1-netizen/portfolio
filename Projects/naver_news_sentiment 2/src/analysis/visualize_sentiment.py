import os
import pandas as pd
import matplotlib.pyplot as plt

########################################
# 0. 경로 설정
########################################

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # .../src/analysis
SRC_DIR = os.path.dirname(BASE_DIR)                     # .../src
ROOT_DIR = os.path.dirname(SRC_DIR)                     # project root
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
FIG_DIR = os.path.join(ROOT_DIR, "data", "figures")


########################################
# 1. 데이터 불러오기
########################################

def load_processed_comments(csv_name="comments_with_sentiment_hate.csv"):
    csv_path = os.path.join(PROCESSED_DIR, csv_name)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"{csv_path} 파일을 찾을 수 없습니다.")

    df = pd.read_csv(csv_path)
    if "sentiment" not in df.columns:
        raise KeyError("데이터에 'sentiment' 컬럼이 없습니다. sentiment_analysis.py 실행 여부 확인 필요.")
    if "is_hate" not in df.columns:
        raise KeyError("데이터에 'is_hate' 컬럼이 없습니다. text_analysis.py 실행 여부 확인 필요.")
    return df


########################################
# 2. 전체 감정 분포 시각화
########################################

def plot_sentiment_distribution(df: pd.DataFrame):
    counts = df["sentiment"].value_counts().reindex(["긍정", "중립", "부정"]).fillna(0)

    os.makedirs(FIG_DIR, exist_ok=True)
    save_path = os.path.join(FIG_DIR, "sentiment_distribution.png")

    plt.figure()
    counts.plot(kind="bar")
    plt.title("댓글 감정 분포")
    plt.xlabel("감정")
    plt.ylabel("댓글 수")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

    print(f"📊 감정 분포 그래프 저장: {save_path}")


########################################
# 3. 전체 악성 댓글 비율 시각화
########################################

def plot_hate_ratio(df: pd.DataFrame):
    # is_hate: 0/1 이라고 가정
    hate_counts = df["is_hate"].value_counts().sort_index()
    # 인덱스를 보기 좋게 바꾸기
    hate_counts.index = ["정상", "악성"] if len(hate_counts) == 2 else hate_counts.index

    os.makedirs(FIG_DIR, exist_ok=True)
    save_path = os.path.join(FIG_DIR, "hate_ratio.png")

    plt.figure()
    hate_counts.plot(kind="bar")
    plt.title("악성 댓글 비율")
    plt.xlabel("댓글 유형")
    plt.ylabel("댓글 수")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

    print(f"📊 악성 댓글 비율 그래프 저장: {save_path}")


########################################
# 4. (선택) 기사/제목별 요약 시각화
########################################

def plot_article_level_summary(df: pd.DataFrame):
    """
    article_title 또는 news_title 컬럼이 있을 경우,
    기사별로 댓글 수 / 악성 비율을 상위 몇 개만 시각화
    """
    title_col = None
    for c in ["article_title", "news_title", "title"]:
        if c in df.columns:
            title_col = c
            break

    if title_col is None:
        print("⚠️ 기사 제목 컬럼(article_title/news_title/title)이 없습니다. article_url 기준으로 기사 단위 요약을 시도합니다.")
        title_col = "article_url" if "article_url" in df.columns else None
        if title_col is None:
            print("⚠️ article_url 컬럼도 없어 기사 단위 시각화는 건너뜁니다.")
            return

    # 기사별 집계
    group = df.groupby(title_col).agg(
        n_comments=("comment", "count"),
        hate_ratio=("is_hate", "mean"),
    )

    # 댓글 수 상위 10개 기사만
    top = group.sort_values("n_comments", ascending=False).head(10)

    # 1) 기사별 댓글 수 막대그래프
    save_path1 = os.path.join(FIG_DIR, "top_articles_n_comments.png")
    plt.figure(figsize=(10, 5))
    top["n_comments"].plot(kind="bar")
    plt.title("댓글 수 상위 10개 기사")
    plt.ylabel("댓글 수")
    plt.tight_layout()
    plt.savefig(save_path1)
    plt.close()
    print(f"📊 기사별 댓글 수 그래프 저장: {save_path1}")

    # 2) 기사별 악성 댓글 비율 막대그래프
    save_path2 = os.path.join(FIG_DIR, "top_articles_hate_ratio.png")
    plt.figure(figsize=(10, 5))
    top["hate_ratio"].plot(kind="bar")
    plt.title("상위 10개 기사 악성 댓글 비율")
    plt.ylabel("악성 댓글 비율")
    plt.tight_layout()
    plt.savefig(save_path2)
    plt.close()
    print(f"📊 기사별 악성 댓글 비율 그래프 저장: {save_path2}")


########################################
# 4-1. (v2) 리스크 상위 기사 시각화
########################################

def plot_top_risk_articles():
    """If article_sentiment_summary.csv exists, plot Top-N risk_score."""
    summary_path = os.path.join(PROCESSED_DIR, "article_sentiment_summary.csv")
    if not os.path.exists(summary_path):
        print("⚠️ article_sentiment_summary.csv 이 없어 리스크 Top 기사 시각화는 건너뜁니다. (article_level_analysis.py 실행 여부 확인)")
        return

    s = pd.read_csv(summary_path)
    if "risk_score" not in s.columns:
        print("⚠️ risk_score 컬럼이 없어 리스크 Top 기사 시각화를 건너뜁니다.")
        return

    top = s.sort_values(["risk_score", "n_comments"], ascending=[False, False]).head(10)
    label_col = "article_url"

    os.makedirs(FIG_DIR, exist_ok=True)
    save_path = os.path.join(FIG_DIR, "top_articles_risk_score.png")
    plt.figure(figsize=(10, 5))
    top.set_index(label_col)["risk_score"].plot(kind="bar")
    plt.title("리스크 점수 상위 10개 기사")
    plt.ylabel("risk_score")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

    print(f"📊 리스크 Top 기사 그래프 저장: {save_path}")


########################################
# 5. 메인 실행
########################################

def main():
    print("📂 감정+악성 분석 결과 불러오는 중...")
    df = load_processed_comments("comments_with_sentiment_hate.csv")
    print(f"불러온 데이터 수: {len(df)}")

    print("📊 감정 분포 시각화 생성...")
    plot_sentiment_distribution(df)

    print("📊 악성 댓글 비율 시각화 생성...")
    plot_hate_ratio(df)

    print("📊 기사 단위 요약 시각화(가능한 경우)...")
    plot_article_level_summary(df)

    print("📊 (v2) 리스크 상위 기사 시각화(가능한 경우)...")
    plot_top_risk_articles()

    print("✅ 시각화 단계 완료! data/figures 폴더를 확인하세요.")


if __name__ == "__main__":
    main()
