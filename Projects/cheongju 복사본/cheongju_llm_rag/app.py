import os
import streamlit as st
from dotenv import load_dotenv
from preprocess import load_accidents_csv, basic_summary
from rag_engine import RAGEngine

st.set_page_config(page_title="Accident Risk RAG", layout="wide")

def main():
    load_dotenv()

    st.title("🚦 교통사고 리스크 요약 & 대응전략 (LLM-RAG)")

    with st.sidebar:
        st.header("1) 데이터 업로드")
        uploaded = st.file_uploader(
        "사고 데이터 업로드 (csv / xlsx)",
        type=["csv", "xlsx", "xls"]
    )
        st.header("2) 질문")
        question = st.text_area("예: 청원구에서 야간 교차로 사고 위험이 큰 이유와 대책은?", height=100)
        k = st.slider("검색 컨텍스트 개수(k)", 2, 8, 4)

        run_btn = st.button("분석 실행")

    # RAG 로드
    rag = RAGEngine()
    try:
        rag.load()
    except Exception as e:
        st.warning("지식 인덱스가 없어 보여. 먼저 `python ingest.py` 실행해줘.")
        st.stop()

    if run_btn:
        if uploaded is None:
            st.error("CSV를 업로드해줘.")
            st.stop()
        if not question.strip():
            st.error("질문을 입력해줘.")
            st.stop()

         # 🔴 파일 로딩 에러를 화면에서 보여주기
        try:
            df = load_accidents_csv(uploaded)
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했어: {e}")
            st.stop()

        stats = basic_summary(df)

        st.subheader("📌 데이터 요약")
        st.json(stats)

        retrieved = rag.retrieve(question, k=k)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📚 검색된 컨텍스트")
            for i, c in enumerate(retrieved, 1):
                st.markdown(f"**#{i}**")
                st.write(c)

        with col2:
            st.subheader("🤖 LLM 답변")
            answer = rag.answer(question, stats, retrieved)
            st.write(answer)

if __name__ == "__main__":
    main()
