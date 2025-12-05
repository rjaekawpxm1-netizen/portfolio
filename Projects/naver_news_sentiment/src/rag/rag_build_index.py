import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

# ============================
# 1. 데이터 로드
# ============================
def load_comments():
    # 감정 라벨까지 있는 파일을 우선 사용
    path1 = "./data/processed/comments_with_sentiment.csv"
    path2 = "./data/raw/comments_selenium.csv"

    if os.path.exists(path1):
        df = pd.read_csv(path1)
    elif os.path.exists(path2):
        df = pd.read_csv(path2)
    else:
        raise FileNotFoundError("댓글 CSV를 찾을 수 없습니다.")

    # 컬럼 이름 정리
    cols = {c.lower(): c for c in df.columns}

    comment_col = cols.get("comment", None)
    clean_col = cols.get("comment_clean", None)
    senti_col = cols.get("sentiment", None)
    url_col = cols.get("article_url", None)

    if clean_col is not None:
        text_series = df[clean_col].fillna("")
    elif comment_col is not None:
        text_series = df[comment_col].fillna("")
    else:
        raise ValueError("comment / comment_clean 컬럼을 찾을 수 없습니다.")

    sentiment_series = df[senti_col] if senti_col is not None else None
    url_series = df[url_col] if url_col is not None else None

    docs = []
    for i, text in enumerate(text_series):
        if not isinstance(text, str) or text.strip() == "":
            continue

        meta = {
            "text": text.strip(),
        }
        if sentiment_series is not None:
            meta["sentiment"] = str(sentiment_series.iloc[i])
        if url_series is not None:
            meta["article_url"] = str(url_series.iloc[i])

        docs.append(meta)

    print(f"✅ RAG 인덱싱 대상 문장 수: {len(docs)}")
    return docs


# ============================
# 2. 임베딩 생성 및 FAISS 인덱스 저장
# ============================
def build_index(docs):
    model = SentenceTransformer("jhgan/ko-sroberta-multitask")

    texts_for_embed = []
    for d in docs:
        base = d["text"]
        senti = d.get("sentiment")
        if senti and senti != "nan":
            base = f"[{senti}] {base}"
        texts_for_embed.append(base)

    print("🔍 임베딩 생성 중...")
    embeddings = model.encode(texts_for_embed, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings.astype(np.float32))

    os.makedirs("./data/rag", exist_ok=True)

    index_path = "./data/rag/comments.index"
    docs_path = "./data/rag/comments_docs.pkl"

    faiss.write_index(index, index_path)
    with open(docs_path, "wb") as f:
        pickle.dump(docs, f)

    print(f"📦 FAISS 인덱스 저장: {index_path}")
    print(f"📦 문서 메타 저장: {docs_path}")
    print("🎉 RAG 인덱스 생성 완료!")


if __name__ == "__main__":
    docs = load_comments()
    build_index(docs)
