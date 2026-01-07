# evaluate_rag.py
from rag_engine import RAGEngine
import config

TEST_CASES = [
    {
        "question": "청주시에서 야간(22~02시) 보행자 사고의 주요 위험 요인은?",
        "expect_keywords": ["야간", "보행자", "22시", "02시"],  # 대략적인 키워드
    },
    {
        "question": "우천 시 교차로에서 사고가 자주 나는 이유는?",
        "expect_keywords": ["우천", "교차로"],
    },
    # 필요하면 5~10개 정도 더 추가
]

def main():
    rag = RAGEngine()
    rag.load_index()

    total = len(TEST_CASES)
    hit = 0

    for case in TEST_CASES:
        q = case["question"]
        kws = case["expect_keywords"]

        retrieved = rag.retrieve(q, k=config.TOP_K)
        joined = " ".join(retrieved)

        ok = all(kw in joined for kw in kws)
        if ok:
            hit += 1
        print(f"[{'O' if ok else 'X'}] {q} -> {kws}")

    print(f"\nRetrieval Hit Rate: {hit}/{total} = {hit/total:.2f}")

if __name__ == "__main__":
    main()
