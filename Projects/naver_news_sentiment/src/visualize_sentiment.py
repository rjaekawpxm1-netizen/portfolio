import os
import pandas as pd
import matplotlib.pyplot as plt

########################################
# 0. 한글 폰트 설정 (Windows 기준)
########################################
plt.rcParams["font.family"] = "Malgun Gothic"  # 맑은 고딕
plt.rcParams["axes.unicode_minus"] = False     # 마이너스 깨짐 방지

########################################
# 1. 데이터 불러오기
########################################
DATA_PATH = "../data/processed/comments_with_sentiment.csv"

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"{DATA_PATH} 파일을 찾을 수 없습니다. 먼저 sentiment_analysis.py를 실행하세요.")

df = pd.read_csv(DATA_PATH)
print(f"[INFO] 불러온 데이터 수: {len(df)}")
print(df.head())

os.makedirs("../data/figures", exist_ok=True)

########################################
# 2. 전체 감정 비율 막대그래프
########################################
sentiment_counts = df["sentiment"].value_counts().reindex(["긍정", "중립", "부정"]).fillna(0)

plt.figure(figsize=(6, 4))
sentiment_counts.plot(kind="bar")
plt.title("전체 댓글 감정 분포")
plt.xlabel("감정")
plt.ylabel("댓글 수")
plt.tight_layout()
overall_path = "../data/figures/sentiment_overall_bar.png"
plt.savefig(overall_path, dpi=150)
plt.close()
print(f"[DONE] 전체 감정 분포 그래프 저장: {overall_path}")

########################################
# 3. 기사별 감정 분포 (상위 N개 기사만)
########################################
# 기사 URL이 너무 길어서 article_id 만들어서 사용
df["article_id"] = df["article_url"].factorize()[0] + 1  # 1,2,3,...

# 기사별 댓글 수 기준 상위 N개만 보기
TOP_N = 10
top_articles = (
    df.groupby("article_id")["comment"]
    .count()
    .sort_values(ascending=False)
    .head(TOP_N)
    .index
)

df_top = df[df["article_id"].isin(top_articles)]

# 기사별-감정별 카운트 피벗
pivot = (
    df_top.pivot_table(
        index="article_id",
        columns="sentiment",
        values="comment",
        aggfunc="count",
        fill_value=0,
    )
    .reindex(columns=["긍정", "중립", "부정"])
)

plt.figure(figsize=(8, 5))
pivot.plot(kind="bar", stacked=True)
plt.title(f"기사별 감정 분포 (상위 {TOP_N}개 기사)")
plt.xlabel("기사 ID")
plt.ylabel("댓글 수")
plt.xticks(rotation=0)
plt.tight_layout()
article_path = "../data/figures/sentiment_by_article_stacked.png"
plt.savefig(article_path, dpi=150)
plt.close()
print(f"[DONE] 기사별 감정 분포 그래프 저장: {article_path}")

########################################
# 4. 감정별 평균 좋아요 수 (선택)
########################################
if "like" in df.columns:
    df["like"] = pd.to_numeric(df["like"], errors="coerce").fillna(0)
    like_mean = df.groupby("sentiment")["like"].mean().reindex(["긍정", "중립", "부정"])

    plt.figure(figsize=(6, 4))
    like_mean.plot(kind="bar")
    plt.title("감정별 평균 좋아요 수")
    plt.xlabel("감정")
    plt.ylabel("평균 좋아요")
    plt.tight_layout()
    like_path = "../data/figures/sentiment_like_mean_bar.png"
    plt.savefig(like_path, dpi=150)
    plt.close()
    print(f"[DONE] 감정별 평균 좋아요 그래프 저장: {like_path}")

print("\n✅ 모든 시각화 완료!  data/figures 폴더에서 이미지를 확인하세요.")
