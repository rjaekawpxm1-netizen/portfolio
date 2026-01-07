import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"

SYSTEM = """너는 데이터 분석 결과를 '붙여넣기 쉬운 문장'으로 만드는 에디터다.
사용자가 제공한 JSON 수치만 근거로 작성한다.
원인 단정 금지, 과한 추측 금지.
문장은 짧고 명확하게, 한국어로 쓴다.
"""

PROMPT = """아래 JSON은 청주시/전국 교통사고 요약 지표다.
Power BI에 붙일 수 있도록 '캡션/멘트'를 JSON으로만 출력해라.

요구 출력(JSON 스키마):
{{
  "kpi_caption": {{"short":"", "medium":"", "long":""}},
  "fatality_ratio_bar_caption": {{"short":"", "medium":"", "long":""}},
  "severity_donut_cheongju_caption": {{"short":"", "medium":"", "long":""}},
  "severity_donut_national_caption": {{"short":"", "medium":"", "long":""}},
  "scatter_caption": {{"short":"", "medium":"", "long":""}},
  "presentation_script": {{"10s":"", "20s":"", "40s":""}},
  "limitations": ["", "", ""]
}}

조건:
- short는 1문장, medium은 2문장, long은 3~4문장
- limitations는 '이 데이터로는 말할 수 없는 것' 3개를 짧게

JSON:
{metrics_json}
"""


def main():
    load_dotenv()
    client = OpenAI()

    metrics = (OUT / "metrics.json").read_text(encoding="utf-8")

    resp = client.responses.create(
        model="gpt-5.2",
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": PROMPT.format(metrics_json=metrics)},
        ],
    )

    # 모델이 JSON만 내도록 유도했지만 혹시 모를 잡텍스트 제거용 최소 처리
    text = resp.output_text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("LLM output is not JSON. Output:\n" + text)

    captions = json.loads(text[start:end+1])
    (OUT / "captions.json").write_text(json.dumps(captions, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Saved:", OUT / "captions.json")

if __name__ == "__main__":
    main()
