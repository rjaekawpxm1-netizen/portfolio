import os
from dotenv import load_dotenv
from rag_engine import RAGEngine

def main():
    load_dotenv()
    kb_dir = "data/kb"
    files = [os.path.join(kb_dir, f) for f in os.listdir(kb_dir) if f.endswith(".txt")]
    if not files:
        raise FileNotFoundError("data/kb 폴더에 .txt 지식 문서가 없음")

    rag = RAGEngine()
    rag.build_from_text_files(files)
    print(f"[OK] 인덱싱 완료: {len(files)}개 파일")

if __name__ == "__main__":
    main()
