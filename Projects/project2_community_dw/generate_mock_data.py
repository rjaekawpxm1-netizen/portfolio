import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import random

# -------------------------------------------------
# 경로 설정 (이 파일을 project2_community_dw 폴더에 둘 것)
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data_raw"

DATA_DIR.mkdir(exist_ok=True)

# -------------------------------------------------
# 1. 사용자 더미 데이터 생성
# -------------------------------------------------
n_users = 200
user_ids = np.arange(1, n_users + 1)

genders = np.random.choice(["M", "F"], size=n_users)
ages = np.random.randint(18, 50, size=n_users)
regions = np.random.choice(["Seoul", "Busan", "Incheon", "Daegu", "Daejeon"], size=n_users)

start_signup = datetime(2024, 1, 1)
end_signup = datetime(2024, 3, 31)
signup_range_days = (end_signup - start_signup).days

signup_dates = [
    (start_signup + timedelta(days=int(random.random() * signup_range_days))).date()
    for _ in range(n_users)
]

users = pd.DataFrame({
    "user_id": user_ids,
    "gender": genders,
    "age": ages,
    "signup_date": signup_dates,
    "region": regions,
})

# -------------------------------------------------
# 2. 카테고리/게시글 더미 데이터 생성
# -------------------------------------------------
categories_list = ["Free", "QnA", "Study", "Review", "Notice"]
categories = pd.DataFrame({
    "category_id": range(1, len(categories_list) + 1),
    "category_name": categories_list,
})

n_posts = 1000
post_ids = np.arange(1, n_posts + 1)

category_ids = np.random.choice(categories["category_id"], size=n_posts)
author_ids = np.random.choice(users["user_id"], size=n_posts)
device_types = np.random.choice(["PC", "Mobile"], size=n_posts)

start_post = datetime(2024, 1, 1)
end_post = datetime(2024, 6, 30)
post_range_days = (end_post - start_post).days

created_at = [
    start_post + timedelta(
        days=int(random.random() * post_range_days),
        seconds=int(random.random() * 86400)
    )
    for _ in range(n_posts)
]

posts = pd.DataFrame({
    "post_id": post_ids,
    "category_id": category_ids,
    "author_id": author_ids,
    "created_at": created_at,
    "device_type": device_types,
})

# -------------------------------------------------
# 3. 행동 로그(fact) 더미 데이터 생성
# -------------------------------------------------
n_actions = 30000

action_ids = np.arange(1, n_actions + 1)
action_user_ids = np.random.choice(users["user_id"], size=n_actions)
action_post_ids = np.random.choice(posts["post_id"], size=n_actions)

action_types = np.random.choice(
    ["view", "like", "comment", "share"],
    size=n_actions,
    p=[0.7, 0.15, 0.1, 0.05]
)

# post의 created_at 기준으로 +/- 60일 안에서 액션 발생
posts_created_at_map = dict(zip(posts["post_id"], posts["created_at"]))

action_timestamps = []
for pid in action_post_ids:
    base_time = posts_created_at_map[pid]
    offset_days = np.random.randint(0, 60)
    offset_seconds = np.random.randint(0, 86400)
    action_timestamps.append(base_time + timedelta(days=offset_days, seconds=offset_seconds))

session_ids = [f"s{np.random.randint(1, 5000)}" for _ in range(n_actions)]

actions = pd.DataFrame({
    "action_id": action_ids,
    "user_id": action_user_ids,
    "post_id": action_post_ids,
    "action_type": action_types,
    "action_timestamp": action_timestamps,
    "session_id": session_ids,
})

# -------------------------------------------------
# 4. 전체 테이블 병합 (users + posts + categories + actions)
# -------------------------------------------------
posts_full = posts.merge(categories, on="category_id", how="left")

full = (
    actions
    .merge(users, on="user_id", how="left")
    .merge(posts_full, on="post_id", how="left")
)

# -------------------------------------------------
# 5. CSV 저장
# -------------------------------------------------
output_path = DATA_DIR / "community_dw_full.csv"
full.to_csv(output_path, index=False)

print("===== 더미 데이터 생성 완료 =====")
print(f"사용자 수: {len(users)}")
print(f"게시글 수: {len(posts)}")
print(f"행동 로그 수: {len(actions)}")
print(f"저장 파일: {output_path}")
print(f"액션 날짜 범위: {full['action_timestamp'].min()} ~ {full['action_timestamp'].max()}")
