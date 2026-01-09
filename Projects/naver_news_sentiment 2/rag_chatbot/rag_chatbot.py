import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
import os

# API 불러오기
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1) VectorDB 로드
index = faiss.read_index("comments.index")
with open("comments_texts.pkl", "rb") as f:
    texts = pickle.load(f)

# 2) 같은 임베딩 모델
embed_model = SentenceTransformer("jhgan/ko-sroberta-multitask")

def search_similar_comments(query, top_k=5):
    q_emb = embed_model.encode([query])
    distances, indices = index.search(q_emb, top_k)
    results = [texts[i] for i in indices[0]]
    return results

def ask_llm(query):
    relevant_comments = search_similar_comments(query)

    prompt = f"""
다음은 뉴스 댓글 데이터에서 가져온 관련 문장들이야:

{relevant_comments}

위 문장을 참고해서 아래 질문에 한국어로 답해줘.

질문: {query}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message.content

# 실행
if __name__ == "__main__":
    print("🧠 댓글 기반 Q&A 챗봇 시작")

    while True:
        query = input("\n질문 입력 (exit 입력하면 종료): ")
        if query.lower() == "exit":
            break
        
        answer = ask_llm(query)
        print("\n🤖 답변:", answer)
