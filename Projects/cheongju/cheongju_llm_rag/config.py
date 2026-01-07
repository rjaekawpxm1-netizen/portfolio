# config.py

# ===== LLM / Embedding 설정 =====
EMBEDDING_MODEL = "text-embedding-3-small"  # 속도/비용/성능 밸런스용
CHAT_MODEL = "gpt-4o-mini"                 # 정책/설명 쓰기 좋은 가벼운 모델
TEMPERATURE = 0.4                          # 일관성 ↑, 랜덤성 ↓

# ===== RAG 설정 =====
CHUNK_SIZE = 200            # 한 컨셉이 잘리는 최소 단위
TOP_K = 4                   # 너무 많으면 노이즈, 너무 적으면 정보 부족

# ===== 입력/출력 길이 의도 (설계 기준) =====
# 실제 max_tokens는 OpenAI API 호출 시 사용 가능
MAX_INPUT_TOKENS = 2048     # 질문 + stats + 컨텍스트가 들어가는 목표 범위
MAX_OUTPUT_TOKENS = 400     # 요약 + 위험요인 + 대응전략 정도 분량

# ===== 파일 경로 =====
INDEX_PATH = "storage/faiss.index"
META_PATH = "storage/meta.json"
POLICY_NOTES_PATH = "data/kb/policy_notes.txt"
