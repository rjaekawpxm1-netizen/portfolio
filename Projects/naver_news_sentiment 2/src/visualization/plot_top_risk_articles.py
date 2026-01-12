import pandas as pd
import matplotlib.pyplot as plt

# 데이터 로드
df = pd.read_csv(
    "data/processed/article_sentiment_summary.csv",
    encoding="utf-8-sig"
)

# 위험도 Top 10 기사 추출
top10 = (
    df.sort_values("risk_score", ascending=False)
      .head(10)
      .reset_index(drop=True)
)

# 순위 컬럼 추가
top10["Rank"] = top10.index + 1

# 그래프 생성
plt.figure(figsize=(10, 5))

plt.barh(
    top10["Rank"].astype(str),
    top10["risk_score"]
)

plt.gca().invert_yaxis()

plt.title("기사 단위 여론 위험도 Top 10", fontsize=14)
plt.xlabel("Risk Score")
plt.ylabel("Rank")

# 점수 표시
for i, v in enumerate(top10["risk_score"]):
    plt.text(v + 0.5, i, f"{v:.1f}", va="center")

plt.tight_layout()
plt.savefig(
    "data/figures/top_articles_risk_score_v2.png",
    dpi=300
)

plt.show()
