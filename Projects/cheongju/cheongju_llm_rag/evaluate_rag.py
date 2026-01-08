from dotenv import load_dotenv
load_dotenv()

from rag_engine import RAGEngine
import config

TEST_CASES = [
    {
        "question": "청주시에서 야간(22~02시) 보행자 사고의 주요 위험 요인은?",
        "expect_keywords": ["야간", "보행자"],
    },
    {
        "question": "우천 시 교차로에서 사고가 자주 나는 이유는?",
        "expect_keywords": ["우천", "교차로"],
    },
    {
        "question": "청원구에서 교차로 사고 위험이 큰 이유와 우선 대책은?",
        "expect_keywords": ["청원", "교차로"],
    },
]

def main():
    rag = RAGEngine()
    rag.load()  # ✅ 여기! load_index()가 아니라 load()

    total = len(TEST_CASES)
    hit = 0

    for case in TEST_CASES:
        q = case["question"]
        kws = case["expect_keywords"]

        retrieved = rag.retrieve(q, k=config.TOP_K)
        joined = " ".join(retrieved)

        ok = all(kw in joined for kw in kws)
        hit += int(ok)

        print(f"[{'O' if ok else 'X'}] {q}")
        print(f"  - expect: {kws}")
        print(f"  - top{config.TOP_K} context (snippet): {joined[:160]}...\n")

    print(f"Retrieval Hit Rate: {hit}/{total} = {hit/total:.2f}")

if __name__ == "__main__":
    main()
