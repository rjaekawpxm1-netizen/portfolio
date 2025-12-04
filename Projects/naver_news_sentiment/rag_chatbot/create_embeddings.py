import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

# 1) 데이터 로드
df = pd.read_csv("../data/raw/comments_selenium.csv")
texts = df["comment"].fillna("").tolist()

# 2) 한국어 임베딩 모델
model = SentenceTransformer("jhgan/ko-sroberta-multitask")

# 3) 임베딩 생성
embeddings = model.encode(texts, convert_to_numpy=True)

# 4) VectorDB(faiss) 생성
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embeddings)

# 5) 저장
faiss.write_index(index, "comments.index")

with open("comments_texts.pkl", "wb") as f:
    pickle.dump(texts, f)

print("🎉 임베딩 생성 + 저장 완료!")
