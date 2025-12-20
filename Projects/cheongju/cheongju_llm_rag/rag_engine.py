import os
import json
import numpy as np
import faiss
from openai import OpenAI

def _chunk_text(text: str, chunk_size: int = 300) -> list[str]:
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []

    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size].strip()
        if chunk:
            chunks.append(chunk)

    return chunks


class RAGEngine:
    def __init__(self, index_path="storage/faiss.index", meta_path="storage/meta.json"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embed_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.chat_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        self.index_path = index_path
        self.meta_path = meta_path
        self.index = None
        self.meta = []

    def build_from_text_files(self, file_paths: list[str]):
        texts = []
        for p in file_paths:
            with open(p, "r", encoding="utf-8") as f:
                texts.append(f.read())

        chunks = []
        for t in texts:
            chunks.extend(_chunk_text(t))

        vectors = self._embed(chunks)
        dim = vectors.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(vectors)
        self.index.add(vectors)

        self.meta = [{"chunk": c} for c in chunks]
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)

    def load(self):
        if not os.path.exists(self.index_path) or not os.path.exists(self.meta_path):
            raise FileNotFoundError("인덱스/메타가 없음. 먼저 ingest.py 실행 필요")
        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            self.meta = json.load(f)

    def retrieve(self, query: str, k: int = 4) -> list[str]:
        qv = self._embed([query])
        faiss.normalize_L2(qv)
        scores, idx = self.index.search(qv, k)
        results = []
        for i in idx[0]:
            if i == -1:
                continue
            results.append(self.meta[i]["chunk"])
        return results

    def answer(self, user_question: str, stats_summary: str, retrieved_chunks: list[str]) -> str:
        context = "\n\n---\n\n".join(retrieved_chunks)
        prompt = f"""
너는 교통안전 분석가다. 아래의 '데이터 요약'과 '지식 컨텍스트'를 근거로 사용자의 질문에 답해라.
- 근거가 부족하면 "추가 데이터 필요"를 말하고 어떤 데이터가 필요한지 제시해라.
- 출력은 한국어로, 너무 길지 않게. (핵심 8~12줄)
- 반드시: ①핵심 위험요인 ②왜 위험한지 ③우선 대응전략(3개) ④추가로 확인할 데이터

[데이터 요약]
{stats_summary}

[지식 컨텍스트]
{context}

[사용자 질문]
{user_question}
""".strip()

        resp = self.client.chat.completions.create(
            model=self.chat_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()

    def _embed(self, texts: list[str]) -> np.ndarray:
        resp = self.client.embeddings.create(model=self.embed_model, input=texts)
        vecs = np.array([d.embedding for d in resp.data], dtype="float32")
        return vecs
