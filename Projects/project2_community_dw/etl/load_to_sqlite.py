import sqlite3
import pandas as pd
from pathlib import Path

# ----------------------------------------
# 1. 경로 설정
# ----------------------------------------
# 현재 파일 기준으로 프로젝트 루트 경로 찾기
BASE_DIR = Path(__file__).resolve().parents[1]

DB_PATH = BASE_DIR / "community_dw.db"          # 생성할 SQLite 파일 이름
SQL_PATH = BASE_DIR / "sql" / "01_create_tables.sql"

DATA_RAW_DIR = BASE_DIR / "data_raw"

USERS_CSV = DATA_RAW_DIR / "users.csv"
CATEGORIES_CSV = DATA_RAW_DIR / "categories.csv"
POSTS_CSV = DATA_RAW_DIR / "posts.csv"
ACTIONS_CSV = DATA_RAW_DIR / "actions.csv"

# ----------------------------------------
# 2. SQLite 연결 & 테이블 생성
# ----------------------------------------
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 외래키 제약조건 활성화
cur.execute("PRAGMA foreign_keys = ON;")

# 테이블 생성 SQL 실행
with open(SQL_PATH, "r", encoding="utf-8") as f:
    create_sql = f.read()
cur.executescript(create_sql)
print("[INFO] 테이블 생성 완료")

# ----------------------------------------
# 3. CSV 로드 (Pandas)
# ----------------------------------------
df_users = pd.read_csv(USERS_CSV)
df_categories = pd.read_csv(CATEGORIES_CSV)
df_posts = pd.read_csv(POSTS_CSV)
df_actions = pd.read_csv(ACTIONS_CSV)

print("[INFO] CSV 로드 완료")
print(" - users:", df_users.shape)
print(" - categories:", df_categories.shape)
print(" - posts:", df_posts.shape)
print(" - actions:", df_actions.shape)

# ----------------------------------------
# 4. 테이블에 데이터 적재 (dim -> fact 순서)
# ----------------------------------------
df_users.to_sql("dim_user", conn, if_exists="append", index=False)
df_categories.to_sql("dim_category", conn, if_exists="append", index=False)
df_posts.to_sql("dim_post", conn, if_exists="append", index=False)
df_actions.to_sql("fact_user_action", conn, if_exists="append", index=False)

conn.commit()
print("[INFO] 데이터 적재 완료")

conn.close()
print(f"[INFO] SQLite DB 생성 완료: {DB_PATH}")
