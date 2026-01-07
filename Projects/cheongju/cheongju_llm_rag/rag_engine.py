import os
import json
from typing import List

import numpy as np
import faiss
from openai import OpenAI

import config  # EMBEDDING_MODEL, CHAT_MODEL, CHUNK_SIZE, TOP_K, TEMPERATURE, INDEX_PATH, META_PATH


def _chunk_text(text: str, chunk_size: int | None = None) -> List[str]:
    """
    긴 텍스트를 chunk_size 단위로 잘라 리스트로 반환.
    chunk_size가 None이면 config.CHUNK_SIZE를 사용.
    """
    if chunk_size is None:
        chunk_size = getattr(config, "CHUNK_SIZE", 200)

    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []

    chunks: List[str] = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i : i + chunk_size].strip()
        if chunk:
            chunks.append(chunk)

    return chunks


class RAGEngine:
    def __init__(self, index_path: str | None = None, meta_path: str | None = None):
        # OpenAI 클라이언트 설정
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # 모델 / 설정값은 config에서 통일 관리
        self.embed_model = config.EMBEDDING_MODEL
        self.chat_model = config.CHAT_MODEL

        # 인덱스/메타 파일 경로
        self.index_path = index_path or config.INDEX_PATH
        self.meta_path = meta_path or config.META_PATH

        self.index: faiss.Index | None = None
        self.meta: list[dict] = []

    def build_from_text_files(self, file_paths: List[str]):
        """
        여러 텍스트 파일을 읽어 chunking → 임베딩 → FAISS 인덱스 생성.
        ingest.py에서 사용할 함수.
        """
        texts: List[str] = []
        for p in file_paths:
            with open(p, "r", encoding="utf-8") as f:
                texts.append(f.read())

        chunks: List[str] = []
        for t in texts:
            chunks.extend(_chunk_text(t, chunk_size=config.CHUNK_SIZE))

        if not chunks:
            raise ValueError("생성된 청크가 없습니다. 입력 텍스트를 확인해주세요.")

        vectors = self._embed(chunks)
        dim = vectors.shape[1]

        # Inner Product + L2 Normalize → cosine 유사도와 동일
        self.index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(vectors)
        self.index.add(vectors)

        self.meta = [{"chunk": c} for c in chunks]

        # 저장
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)

    def load(self):
        """
        저장된 FAISS 인덱스와 메타 정보를 로드.
        app.py에서 RAGEngine() 생성 후 바로 호출.
        """
        if not os.path.exists(self.index_path) or not os.path.exists(self.meta_path):
            raise FileNotFoundError("인덱스/메타가 없음. 먼저 ingest.py 실행 필요")

        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            self.meta = json.load(f)

    def retrieve(self, query: str, k: int | None = None) -> List[str]:
        """
        쿼리 문장을 임베딩하여 FAISS 인덱스에서 상위 k개 청크를 검색.
        k가 None이면 config.TOP_K 사용.
        """
        if self.index is None:
            raise RuntimeError("인덱스가 로드되지 않았습니다. 먼저 load()를 호출하세요.")

        k = k or config.TOP_K

        qv = self._embed([query])
        faiss.normalize_L2(qv)
        scores, idx = self.index.search(qv, k)

        results: List[str] = []
        for i in idx[0]:
            if i == -1:
                continue
            results.append(self.meta[i]["chunk"])
        return results

    def answer(self, user_question: str, stats_summary: str, retrieved_chunks: List[str]) -> str:
        """
        데이터 요약 + 검색된 컨텍스트 + 사용자 질문을 합쳐
        LLM에게 질의하고 한국어 답변을 생성.
        """
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
            temperature=config.TEMPERATURE,
            # 필요하면 출력 길이도 통제 가능
            # max_tokens=getattr(config, "MAX_OUTPUT_TOKENS", 400),
        )
        return resp.choices[0].message.content.strip()

    def _embed(self, texts: List[str]) -> np.ndarray:
        """
        텍스트 리스트를 임베딩 벡터(np.ndarray)로 변환.
        """
        resp = self.client.embeddings.create(model=self.embed_model, input=texts)
        vecs = np.array([d.embedding for d in resp.data], dtype="float32")
        return vecs
