import pandas as pd
import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

########################################
# 1. 데이터 로드
########################################
df = pd.read_csv("../data/processed/comments_with_sentiment.csv")

# 혹시 컬럼 이름이 대문자면 아래처럼 맞춰줘야 함:
# df.rename(columns={"Comment": "comment", "Comment Clean": "comment_clean", "Sentiment": "sentiment"}, inplace=True)

if "comment_clean" not in df.columns:
    # comment_clean 없으면 comment 사용
    df["comment_clean"] = df["comment"]

########################################
# 2. 간단 토크나이저 (KoNLPy 없이)
########################################

def clean_text(text):
    text = str(text)
    # 한글/영문/숫자/공백만 남기기
    text = re.sub(r"[^가-힣0-9a-zA-Z ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text):
    text = clean_text(text)
    tokens = text.split()
    # 1글자 토큰 제거 (의미 적음)
    tokens = [t for t in tokens if len(t) > 1]
    return tokens

########################################
# 3. 전체 단어 리스트 만들기
########################################

df["tokens"] = df["comment_clean"].apply(tokenize)

all_words = []
for words in df["tokens"]:
    all_words.extend(words)

########################################
# 4. 전체 단어 빈도 계산
########################################

word_freq = Counter(all_words)
top_words = word_freq.most_common(100)

os.makedirs("../data/processed", exist_ok=True)

freq_path = "../data/processed/word_frequency.csv"
pd.DataFrame(top_words, columns=["word", "count"]).to_csv(
    freq_path, index=False, encoding="utf-8-sig"
)
print(f"✔ 전체 단어 빈도 저장 완료: {freq_path}")

########################################
# 5. 감정별 단어 빈도 분석
########################################

sentiments = ["긍정", "중립", "부정"]
sentiment_word_freq = {}

for s in sentiments:
    temp_df = df[df["sentiment"] == s]
    words = []
    for tokens in temp_df["tokens"]:
        words.extend(tokens)
    freq = Counter(words).most_common(50)
    sentiment_word_freq[s] = freq

    s_path = f"../data/processed/word_freq_{s}.csv"
    pd.DataFrame(freq, columns=["word", "count"]).to_csv(
        s_path, index=False, encoding="utf-8-sig"
    )
    print(f"✔ 감정별 단어 빈도 저장 완료: {s_path}")

########################################
# 6. 워드클라우드 생성
########################################

# 한글 폰트 경로 (윈도우 기준)
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"

wc = WordCloud(
    font_path=FONT_PATH,
    background_color="white",
    width=1000,
    height=600
)

# 전체 워드클라우드
wc.generate_from_frequencies(word_freq)
plt.figure(figsize=(10, 6))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
total_wc_path = "../data/processed/wordcloud_total.png"
plt.savefig(total_wc_path, dpi=150)
plt.close()
print(f"✔ 전체 워드클라우드 저장 완료: {total_wc_path}")

# 감정별 워드클라우드
for s in sentiments:
    freq_dict = dict(sentiment_word_freq[s])
    if not freq_dict:
        continue
    wc.generate_from_frequencies(freq_dict)
    plt.figure(figsize=(10, 6))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    s_wc_path = f"../data/processed/wordcloud_{s}.png"
    plt.savefig(s_wc_path, dpi=150)
    plt.close()
    print(f"✔ {s} 워드클라우드 저장 완료: {s_wc_path}")

print("\n✅ 텍스트 분석 및 워드클라우드 생성 완료!")
