import os
import requests
import pandas as pd
from dotenv import load_dotenv

# .env 불러오기
load_dotenv()

def fetch_accident_data():
    base_url = os.getenv("ODCLOUD_BASE_URL", "https://api.odcloud.kr/api")
    service_key = os.getenv("ODCLOUD_API_KEY")

    if not service_key:
        raise ValueError("ODCLOUD_API_KEY가 설정되어 있지 않습니다. .env 파일을 확인하세요.")

    # 2019년 시도 시군구별 교통사고 통계 (네가 고른 UDDI 엔드포인트)
    endpoint = "/15070297/v1/uddi:fbdc4540-ef0e-4852-9d2d-b151ee9ecb8e"

    url = f"{base_url}{endpoint}"
    params = {
        "page": 1,
        "perPage": 1000,
        "serviceKey": service_key,
    }

    print(f"[INFO] API 요청 URL: {url}")

    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        raise Exception(f"API 호출 실패: {response.status_code}, {response.text}")

    data = response.json()

    # odcloud 형식: {"currentCount":..., "data":[...], "page":..., "perPage":..., "totalCount":...}
    rows = data.get("data", [])
    df = pd.DataFrame(rows)

    print(f"[INFO] 받아온 행 개수: {len(df)}")
    return df
