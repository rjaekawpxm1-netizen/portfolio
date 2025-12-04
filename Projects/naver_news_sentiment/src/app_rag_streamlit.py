import os
import pickle
import faiss
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from openai import OpenAI

# ============================
# 0. 페이지 설정 (항상 첫 Streamlit 명령!)
# ============================
st.set_page_config(page_title="뉴스 댓글 RAG 챗봇", layout="wide")

# ============================
# 1. 환경설정
# ============================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INDEX_PATH = "./data/rag/comments.index"
DOCS_PATH = "./data/rag/comments_docs.pkl"


# ============================
# 2. RAG 리소스 로드 (캐시)
# ============================
@st.cache_resource
def load_rag_objects():
    index = faiss.read_index(INDEX_PATH)
    with open(DOCS_PATH, "rb") as f:
        docs = pickle.load(f)
    embed_model = SentenceTransformer("jhgan/ko-sroberta-multitask")
    return index, docs, embed_model


index, docs, embed_model = load_rag_objects()


# ============================
# 3. 유사 댓글 검색
# ============================
def search_similar_comments(query, top_k=7):
    q_emb = embed_model.encode([query], convert_to_numpy=True).astype(np.float32)
    distances, indices = index.search(q_emb, top_k)

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(docs):
            results.append(docs[idx])
    return results


# ============================
# 4. LLM + RAG 답변
# ============================
def ask_with_rag(query: str):
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
너는 뉴스 기사에 달린 댓글을 분석하는 한국어 데이터 분석가야.

다음은 사용자의 질문과 연관성이 높은 뉴스 댓글 목록이야:

{context_str}

위 댓글들을 '근거'로만 사용해서 아래 질문에 답변해줘.
추측하지 말고, 댓글에서 확인되는 내용만 요약해서 설명해줘.

질문: {query}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    answer = completion.choices[0].message.content
    return answer, relevant


# ============================
# 5. Streamlit UI
# ============================
st.title("🧠 뉴스 댓글 RAG Q&A 챗봇")
st.caption("네이버 뉴스 댓글을 기반으로 질문에 답하는 LLM + RAG 분석 도구")

query = st.text_input(
    "질문을 입력하세요 (예: '전체적으로 댓글 분위기가 어때?', '부정 댓글은 어떤 내용이 많아?')"
)

col1, col2 = st.columns([2, 1])

with col1:
    if st.button("질문하기") and query.strip():
        with st.spinner("댓글을 검색하고 답변을 생성하는 중입니다..."):
            answer, relevant = ask_with_rag(query.strip())

        st.subheader("🤖 챗봇 답변")
        st.write(answer)

        with st.expander("🔎 참고로 사용된 댓글 보기"):
            for i, d in enumerate(relevant, start=1):
                senti = d.get("sentiment", "")
                url = d.get("article_url", "")
                st.markdown(f"**{i}. [{senti}]** {d['text']}")
                if url and url != "nan":
                    st.markdown(
                        f"<small>기사 링크: [{url}]({url})</small>",
                        unsafe_allow_html=True,
                    )

with col2:
    st.subheader("ℹ️ 사용 방법")
    st.markdown(
        """
        - **뉴스 댓글 전체 분위기**가 궁금할 때  
          → `전체적으로 댓글 분위기가 어때?`  
        - **긍정/부정 댓글 내용**이 궁금할 때  
          → `긍정적인 댓글은 어떤 내용이 많아?`  
          → `부정적인 댓글은 주로 무엇을 비판해?`  
        - **특정 기사 느낌**이 궁금할 때  
          → `삼성 관련 기사에 대한 여론은 어때?`  

        질문을 바꿔가면서 여러 번 시도해 보세요 🙂
        """
    )
