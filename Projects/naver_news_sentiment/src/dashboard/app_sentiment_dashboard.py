import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

########################################
# 0. 경로 설정
########################################

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # .../src/dashboard
SRC_DIR = os.path.dirname(BASE_DIR)                     # .../src
ROOT_DIR = os.path.dirname(SRC_DIR)                     # .../naver_news_sentiment

PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")

CSV_NAME_HATE = "comments_with_sentiment_hate.csv"
CSV_NAME_SENT = "comments_with_sentiment.csv"


########################################
# 1. 데이터 로드 (캐시)
########################################

@st.cache_data
def load_data():
    csv_hate = os.path.join(PROCESSED_DIR, CSV_NAME_HATE)
    csv_sent = os.path.join(PROCESSED_DIR, CSV_NAME_SENT)

    if os.path.exists(csv_hate):
        df = pd.read_csv(csv_hate)
        st.caption(f"✅ 불러온 파일: {CSV_NAME_HATE}")
    elif os.path.exists(csv_sent):
        df = pd.read_csv(csv_sent)
        st.warning(f"⚠️ {CSV_NAME_HATE} 파일이 없어 {CSV_NAME_SENT}만 불러왔습니다. (악성 댓글 컬럼 없음)")
    else:
        raise FileNotFoundError(
            f"{csv_hate} 또는 {csv_sent} 파일이 없습니다.\n"
            f"먼저 run_all.py 또는 sentiment_analysis.py를 실행해 주세요."
        )

    if "sentiment" not in df.columns:
        st.warning("'sentiment' 컬럼이 없습니다. sentiment_analysis.py 실행 여부를 확인해 주세요.")
    if "is_hate" not in df.columns:
        st.info("'is_hate' 컬럼이 없어 악성 댓글 관련 그래프는 표시되지 않습니다.")

    return df


########################################
# 2. 메인 앱
########################################

def main():
    st.set_page_config(
        page_title="뉴스 댓글 여론 분석 대시보드",
        layout="wide",
    )

    st.title("📰 뉴스 댓글 여론 분석 대시보드")
    st.caption("네이버 뉴스 기사에 달린 댓글을 기반으로 감정과 악성 댓글을 분석·시각화하는 대시보드입니다.")

    # 데이터 로드
    df = load_data()

    # 기사 제목 컬럼 찾기
    title_col = None
    for c in ["article_title", "news_title", "title"]:
        if c in df.columns:
            title_col = c
            break

    # ===== 탭 설정 =====
    tab_overview, tab_articles = st.tabs(["📊 요약 대시보드", "📰 기사별 분석"])

    # ==============================
    #  [탭 1] 요약 대시보드
    # ==============================
    with tab_overview:
        # 사이드바 필터
        st.sidebar.header("필터 옵션")

        # 기사 선택 (있으면)
        filtered_df = df.copy()
        if title_col is not None:
            article_options = ["전체"] + sorted(filtered_df[title_col].dropna().unique().tolist())
            selected_article = st.sidebar.selectbox("기사 선택", article_options)
            if selected_article != "전체":
                filtered_df = filtered_df[filtered_df[title_col] == selected_article]

        # 감정 필터
        if "sentiment" in filtered_df.columns:
            sentiment_options = ["긍정", "중립", "부정"]
            sentiment_options = [s for s in sentiment_options if s in filtered_df["sentiment"].unique()]
            selected_sentiments = st.sidebar.multiselect(
                "감정 필터",
                options=sentiment_options,
                default=sentiment_options,
            )
            if selected_sentiments:
                filtered_df = filtered_df[filtered_df["sentiment"].isin(selected_sentiments)]

        # 악성 댓글 필터
        if "is_hate" in filtered_df.columns:
            hate_filter = st.sidebar.selectbox(
                "악성 댓글 필터",
                options=["전체", "악성 댓글만", "정상 댓글만"],
                index=0,
            )

            if hate_filter == "악성 댓글만":
                filtered_df = filtered_df[filtered_df["is_hate"] == 1]
            elif hate_filter == "정상 댓글만":
                filtered_df = filtered_df[filtered_df["is_hate"] == 0]

        # 키워드 검색
        if "comment" in filtered_df.columns:
            keyword = st.sidebar.text_input("댓글 내용 키워드 검색")
            if keyword:
                filtered_df = filtered_df[
                    filtered_df["comment"].astype(str).str.contains(keyword, case=False)
                ]

        st.write(f"### 현재 필터 결과: {len(filtered_df)}개 댓글")

        if len(filtered_df) == 0:
            st.warning("조건에 맞는 댓글이 없습니다. 필터를 다시 설정해 주세요.")
        else:
            # 상단 KPI
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("총 댓글 수", f"{len(filtered_df):,}")

            if "sentiment" in filtered_df.columns:
                pos_ratio = (filtered_df["sentiment"] == "긍정").mean() * 100
                neg_ratio = (filtered_df["sentiment"] == "부정").mean() * 100
            else:
                pos_ratio = neg_ratio = 0.0

            with col2:
                st.metric("긍정 비율(%)", f"{pos_ratio:.1f}")

            if "is_hate" in filtered_df.columns:
                hate_ratio = (filtered_df["is_hate"] == 1).mean() * 100
            else:
                hate_ratio = 0.0

            with col3:
                st.metric("악성 댓글 비율(%)", f"{hate_ratio:.1f}")

            st.divider()

            # 그래프
            col_left, col_right = st.columns(2)

            # 감정 분포
            with col_left:
                if "sentiment" in filtered_df.columns:
                    st.subheader("감정 분포")

                    sentiment_counts = (
                        filtered_df["sentiment"].value_counts()
                        .reindex(["긍정", "중립", "부정"])
                        .fillna(0)
                    )

                    fig1, ax1 = plt.subplots()
                    sentiment_counts.plot(kind="bar", ax=ax1)
                    ax1.set_xlabel("감정")
                    ax1.set_ylabel("댓글 수")
                    ax1.set_title("댓글 감정 분포")
                    st.pyplot(fig1)
                else:
                    st.info("감정 정보를 찾을 수 없어 감정 분포 그래프를 표시할 수 없습니다.")

            # 악성 분포
            with col_right:
                if "is_hate" in filtered_df.columns:
                    st.subheader("악성 댓글 분포")

                    hate_counts = filtered_df["is_hate"].value_counts().sort_index()
                    if len(hate_counts) == 2:
                        hate_counts.index = ["정상", "악성"]

                    fig2, ax2 = plt.subplots()
                    hate_counts.plot(kind="bar", ax=ax2)
                    ax2.set_xlabel("댓글 유형")
                    ax2.set_ylabel("댓글 수")
                    ax2.set_title("악성 댓글 vs 정상 댓글 수")
                    st.pyplot(fig2)
                else:
                    st.info("악성 여부 컬럼이 없어 악성 댓글 분포 그래프를 표시할 수 없습니다.")

            st.divider()

            # 댓글 테이블
            st.subheader("댓글 상세 목록")

            show_cols = []
            for c in ["sentiment", "is_hate", "hate_type", "comment", "comment_clean", title_col]:
                if c is not None and c in filtered_df.columns:
                    show_cols.append(c)

            st.dataframe(
                filtered_df[show_cols].reset_index(drop=True),
                use_container_width=True,
            )

    # ==============================
    #  [탭 2] 기사별 분석
    # ==============================
    with tab_articles:
        st.subheader("📰 기사별 댓글·악성 비율 분석")

        if title_col is None:
            st.info("기사 제목 컬럼(article_title / news_title / title)이 없어 기사별 분석을 표시할 수 없습니다.")
            return

        # 기사별 집계
        group = df.groupby(title_col).agg(
            n_comments=("comment", "count"),
            hate_ratio=("is_hate", "mean") if "is_hate" in df.columns else ("comment", "size"),
        )

        # 악성 댓글 비율이 NaN인 경우 0으로
        if "is_hate" in df.columns:
            group["hate_ratio"] = group["hate_ratio"].fillna(0.0)

        # 댓글 수 상위 기사
        st.markdown("#### 💬 댓글 수가 많은 기사 TOP 10")
        top_by_comments = group.sort_values("n_comments", ascending=False).head(10)

        st.dataframe(
            top_by_comments.reset_index().rename(columns={
                title_col: "기사 제목",
                "n_comments": "댓글 수",
                "hate_ratio": "악성 비율",
            }),
            use_container_width=True,
        )

        fig3, ax3 = plt.subplots(figsize=(10, 5))
        top_by_comments["n_comments"].plot(kind="bar", ax=ax3)
        ax3.set_ylabel("댓글 수")
        ax3.set_title("댓글 수 상위 10개 기사")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig3)

        st.divider()

        # 악성 비율 상위 기사 (댓글 수 너무 적은 기사 제외)
        if "is_hate" in df.columns:
            st.markdown("#### ⚠️ 악성 댓글 비율이 높은 기사 TOP 10 (댓글 수 20개 이상)")

            filtered_group = group[group["n_comments"] >= 20]
            if len(filtered_group) == 0:
                st.info("댓글 수 20개 이상인 기사가 없어 악성 댓글 비율 순위를 계산할 수 없습니다.")
            else:
                top_by_hate = filtered_group.sort_values("hate_ratio", ascending=False).head(10)

                st.dataframe(
                    top_by_hate.reset_index().rename(columns={
                        title_col: "기사 제목",
                        "n_comments": "댓글 수",
                        "hate_ratio": "악성 비율",
                    }),
                    use_container_width=True,
                )

                fig4, ax4 = plt.subplots(figsize=(10, 5))
                top_by_hate["hate_ratio"].plot(kind="bar", ax=ax4)
                ax4.set_ylabel("악성 댓글 비율")
                ax4.set_title("악성 댓글 비율 상위 10개 기사")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                st.pyplot(fig4)
        else:
            st.info("is_hate 컬럼이 없어 기사별 악성 댓글 비율 분석을 표시할 수 없습니다.")


if __name__ == "__main__":
    main()
