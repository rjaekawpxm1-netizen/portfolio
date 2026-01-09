import streamlit as st
from data_utils import load_data
from viz_components import (
    render_sentiment_chart,
    render_hate_chart,
    render_wordcloud_section,
    render_kpi_section,
    render_trend_section,
)

import matplotlib.pyplot as plt


def main():
    st.set_page_config(
        page_title="뉴스 댓글 여론 분석 대시보드",
        layout="wide",
    )

    st.title("📰 뉴스 댓글 여론 분석 대시보드")
    st.caption("네이버 뉴스 댓글을 기반으로 감정과 악성 댓글을 분석하는 대시보드입니다.")

    df = load_data()

    # 기사 제목 컬럼 감지
    title_col = None
    for c in ["article_title", "news_title", "title"]:
        if c in df.columns:
            title_col = c
            break

    # 탭 구성
    tab_overview, tab_articles, tab_keywords = st.tabs(
        ["📊 요약 대시보드", "📰 기사별 분석", "☁ 키워드 분석"]
    )

    # --------------------------------------------- #
    # 1) 요약 탭
    # --------------------------------------------- #
    with tab_overview:

        st.sidebar.header("필터 옵션")
        filtered_df = df.copy()

        # 기사 선택
        if title_col is not None:
            options = ["전체"] + sorted(df[title_col].dropna().unique().tolist())
            selected_article = st.sidebar.selectbox("기사 선택", options)
            if selected_article != "전체":
                filtered_df = filtered_df[filtered_df[title_col] == selected_article]

        # 감정 필터
        sentiment_opts = ["긍정", "중립", "부정"]
        sentiment_opts = [s for s in sentiment_opts if s in filtered_df["sentiment_ui"].unique()]
        selected_sentiments = st.sidebar.multiselect(
            "감정 선택",
            sentiment_opts,
            default=sentiment_opts,
        )
        filtered_df = filtered_df[filtered_df["sentiment_ui"].isin(selected_sentiments)]

        # 악성 필터
        if "is_hate" in df.columns:
            hate_filter = st.sidebar.selectbox(
                "악성 댓글",
                ["전체", "악성만", "정상만"],
                index=0,
            )
            if hate_filter == "악성만":
                filtered_df = filtered_df[filtered_df["is_hate"] == 1]
            elif hate_filter == "정상만":
                filtered_df = filtered_df[filtered_df["is_hate"] == 0]

        # 키워드 검색
        keyword = st.sidebar.text_input("댓글 검색")
        if keyword:
            filtered_df = filtered_df[
                filtered_df["comment"].astype(str).str.contains(keyword, case=False)
            ]

        # KPI 영역
        render_kpi_section(filtered_df)

        # 감정 그래프
        render_sentiment_chart(filtered_df)

        # 악성 그래프
        if "is_hate" in filtered_df.columns:
            render_hate_chart(filtered_df)

        # 날짜별 추세
        render_trend_section(filtered_df)

        # 댓글 테이블
        st.subheader("댓글 상세 목록")
        show_cols = ["sentiment_ui", "sentiment", "is_hate", "hate_type", "comment"]
        show_cols = [col for col in show_cols if col in filtered_df.columns]
        st.dataframe(filtered_df[show_cols].reset_index(drop=True), use_container_width=True)

    # --------------------------------------------- #
    # 2) 기사별 분석 탭
    # --------------------------------------------- #
    with tab_articles:
        st.subheader("📰 기사별 분석")

        if title_col is None:
            st.info("기사 제목 컬럼이 없어 분석할 수 없습니다.")
        else:
            group_cols = {"n_comments": ("comment", "count")}
            if "is_hate" in df.columns:
                group_cols["hate_ratio"] = ("is_hate", "mean")

            group = df.groupby(title_col).agg(**group_cols).reset_index()

            st.markdown("#### 💬 댓글 수 TOP 10 기사")
            top10 = group.sort_values("n_comments", ascending=False).head(10)
            st.dataframe(top10, use_container_width=True)

            fig, ax = plt.subplots(figsize=(10, 5))
            top10.set_index(title_col)["n_comments"].plot(kind="bar", ax=ax)
            ax.set_title("댓글 수 상위 10개 기사")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)

            if "hate_ratio" in group.columns:
                st.markdown("#### ⚠️ 악성 댓글 비율 TOP 10 (댓글 ≥ 20개 기사)")
                over20 = group[group["n_comments"] >= 20]
                top_hate = over20.sort_values("hate_ratio", ascending=False).head(10)
                st.dataframe(top_hate, use_container_width=True)

    # --------------------------------------------- #
    # 3) 키워드 분석 (워드클라우드)
    # --------------------------------------------- #
    with tab_keywords:
        render_wordcloud_section(df)


if __name__ == "__main__":
    main()
