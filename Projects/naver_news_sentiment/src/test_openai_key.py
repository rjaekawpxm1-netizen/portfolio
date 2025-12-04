from dotenv import load_dotenv
import os

# 중요: .env 파일 경로 명시
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
print("🔍 env_path:", env_path)

load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("✅ OPENAI_API_KEY 로드 성공")
else:
    print("⚠️ OPENAI_API_KEY 를 못 찾았습니다. .env 위치/내용 확인 필요")
