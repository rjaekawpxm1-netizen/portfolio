import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"

SYSTEM = """너는 데이터 분석 보고서 작성 보조자다.
사용자가 제공한 지표(숫자)만 근거로 해석한다.
모르는 원인/추측(예: 도로 구조, 날씨 등)은 단정하지 말고 '가능한 해석'이라고 표현한다.
출력은 한국어, 짧고 읽기 쉬운 문장으로 쓴다.
"""

PROMPT = """아래 JSON은 '청주시'와 '전국'의 교통사고 심각도 구성(사망/중상/경상/부상신고) 요약이다.

요구 출력(마크다운):
1) 한 문단 요약(3~5문장): 청주 vs 전국 비교 핵심
2) 도넛 차트 해석 문장 4개: (청주 도넛 2문장 + 전국 도넛 2문장)
3) 발표 멘트 20초 버전(구어체 3~4문장)
4) 주의 문장 1개: "이 데이터로는 무엇을 말할 수 없는지" (예: 원인 단정 금지)

JSON:
{metrics_json}
"""

def main():
    load_dotenv()
    client = OpenAI()

    metrics = (OUT / "metrics.json").read_text(encoding="utf-8")

    response = client.responses.create(
        model="gpt-5.2",  # 너 계정/프로젝트에서 사용 가능한 모델로 바꿔도 됨
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": PROMPT.format(metrics_json=metrics)},
        ],
    )

    text = response.output_text
    (OUT / "report.md").write_text(text, encoding="utf-8")
    print("Saved:", OUT / "report.md")

if __name__ == "__main__":
    main()
