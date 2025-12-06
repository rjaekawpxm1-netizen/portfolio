import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud

FONT_PATH = "C:/Windows/Fonts/malgun.ttf"


# ------------------------------ #
# KPI 영역
# ------------------------------ #
def render_kpi_section(df):
    st.subheader("요약 지표")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("총 댓글 수", f"{len(df):,}")

    with col2:
        pos_ratio = (df["sentiment_ui"] == "긍정").mean() * 100
        st.metric("긍정 비율", f"{pos_ratio:.1f}%")

    with col3:
        if "is_hate" in df.columns:
            hate_ratio = (df["is_hate"] == 1).mean() * 100
            st.metric("악성 댓글 비율", f"{hate_ratio:.1f}%")
        else:
            st.metric("악성 댓글 비율", "N/A")


# ------------------------------ #
# 감정 그래프
# ------------------------------ #
def render_sentiment_chart(df):
    st.subheader("감정 분포")

    counts = df["sentiment_ui"].value_counts().reindex(["긍정", "중립", "부정"]).fillna(0)

    fig, ax = plt.subplots()
    counts.plot(kind="bar", ax=ax)
    ax.set_title("댓글 감정 분포")
    st.pyplot(fig)


# ------------------------------ #
# 악성 그래프
# ------------------------------ #
def render_hate_chart(df):
    st.subheader("악성 댓글 분포")

    counts = df["is_hate"].value_counts().sort_index()
    counts.index = ["정상", "악성"]

    fig, ax = plt.subplots()
    counts.plot(kind="bar", ax=ax)
    ax.set_title("악성 vs 정상 댓글")
    st.pyplot(fig)


# ------------------------------ #
# 날짜별 여론 추이
# ------------------------------ #
def render_trend_section(df):
    if "date_for_trend" not in df.columns:
        return

    st.subheader("📅 날짜별 여론 추이")

    tdf = (
        df.groupby("date_for_trend")
        .agg(
            n_comments=("comment", "count"),
            pos_ratio=("sentiment_ui", lambda s: (s == "긍정").mean() * 100),
        )
    )

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        tdf["n_comments"].plot(ax=ax)
        ax.set_title("날짜별 댓글 수")
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots()
        tdf["pos_ratio"].plot(ax=ax)
        ax.set_title("날짜별 긍정 비율")
        st.pyplot(fig)


# ------------------------------ #
# 워드클라우드 섹션
# ------------------------------ #
def render_wordcloud_section(df):

    st.subheader("☁ 키워드 분석 (워드클라우드)")

    text = df["comment"].dropna().astype(str).values
    joined = " ".join(text)

    wc = WordCloud(
        width=800, height=400, background_color="white", font_path=FONT_PATH
    ).generate(joined)

    fig, ax = plt.subplots()
    ax.imshow(wc)
    ax.axis("off")

    st.pyplot(fig)
