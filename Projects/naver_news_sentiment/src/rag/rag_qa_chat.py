import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from openai import OpenAI

# .env 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================
# 1. 인덱스 & 문서 로드
# ============================
INDEX_PATH = "./data/rag/comments.index"
DOCS_PATH = "./data/rag/comments_docs.pkl"

print("📂 FAISS 인덱스 로드 중...")
index = faiss.read_index(INDEX_PATH)

print("📂 문서 메타 로드 중...")
with open(DOCS_PATH, "rb") as f:
    docs = pickle.load(f)

embed_model = SentenceTransformer("jhgan/ko-sroberta-multitask")


# ============================
# 2. 유사 댓글 검색 함수
# ============================
def search_similar_comments(query, top_k=5):
    q_emb = embed_model.encode([query], convert_to_numpy=True).astype(np.float32)
    distances, indices = index.search(q_emb, top_k)

    results = []
    for rank, idx in enumerate(indices[0]):
        if idx < 0 or idx >= len(docs):
            continue
        d = docs[idx]
        results.append(d)
    return results


# ============================
# 3. LLM에게 질의 + 근거 전달
# ============================
def ask_with_rag(query):
    relevant = search_similar_comments(query, top_k=7)

    context_lines = []
    for i, d in enumerate(relevant, start=1):
        line = f"{i}. "
        senti = d.get("sentiment")
        if senti and senti != "nan":
            line += f"[감정: {senti}] "
        line += d["text"]
        url = d.get("article_url")
        if url and url != "nan":
            line += f" (기사: {url})"
        context_lines.append(line)

    context_str = "\n".join(context_lines) if context_lines else "관련 댓글을 찾지 못했습니다."

    prompt = f"""
너는 뉴스 댓글 데이터를 분석하는 한국어 데이터 분석가야.

다음은 질문과 연관성이 높은 뉴스 댓글 목록이야:

{context_str}

위 댓글들을 '근거'로만 사용해서 아래 질문에 답변해줘.
추가로 추측하지 말고, 댓글에서 알 수 있는 내용만 요약해서 말해줘.

질문: {query}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return completion.choices[0].message.content, context_str


# ============================
# 4. CLI 인터랙티브 모드
# ============================
if __name__ == "__main__":
    print("🧠 RAG 기반 뉴스 댓글 Q&A 챗봇 시작")
    print("   (종료하려면 exit 입력)\n")

    while True:
        q = input("❓ 질문: ").strip()
        if q.lower() == "exit":
            print("👋 종료합니다.")
            break

        answer, ctx = ask_with_rag(q)
        print("\n[🔎 참고로 사용된 댓글들]")
        print(ctx)
        print("\n🤖 답변:")
        print(answer)
        print("\n" + "-" * 60 + "\n")
