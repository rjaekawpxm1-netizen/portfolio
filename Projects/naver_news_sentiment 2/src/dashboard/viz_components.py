import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc 
import pandas as pd
from wordcloud import WordCloud

import os
import platform

def get_korean_font_path():
    system = platform.system()

    # Windows
    if system == "Windows":
        candidates = [
            r"C:\Windows\Fonts\malgun.ttf",
            r"C:\Windows\Fonts\malgunsl.ttf",
        ]
        for p in candidates:
            if os.path.exists(p):
                return p

    # macOS
    if system == "Darwin":
        candidates = [
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/Library/Fonts/AppleGothic.ttf",
        ]
        for p in candidates:
            if os.path.exists(p):
                return p

    # Linux(옵션)
    candidates = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothicCoding.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p

    return None

FONT_PATH = get_korean_font_path()

# 폰트 설정 (matplotlib)
if FONT_PATH:
    font_name = font_manager.FontProperties(fname=FONT_PATH).get_name()
    rc("font", family=font_name)

# 마이너스 기호 깨짐 방지
plt.rcParams["axes.unicode_minus"] = False


# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False


# ================================
# 1) KPI 영역
# ================================
def render_kpi_section(df: pd.DataFrame):
    st.subheader("요약 지표")

    col1, col2, col3 = st.columns(3)

    # 총 댓글 수
    with col1:
        st.metric("총 댓글 수", f"{len(df):,}")

    # 긍정 비율
    with col2:
        if "sentiment_ui" in df.columns:
            pos_ratio = (df["sentiment_ui"] == "긍정").mean() * 100
        else:
            pos_ratio = 0.0
        st.metric("긍정 비율", f"{pos_ratio:.1f}%")

    # 악성 비율
    with col3:
        if "is_hate" in df.columns:
            hate_ratio = (df["is_hate"] == 1).mean() * 100
            st.metric("악성 댓글 비율", f"{hate_ratio:.1f}%")
        else:
            st.metric("악성 댓글 비율", "N/A")


# ================================
# 2) 감정 분포 막대그래프
# ================================
def render_sentiment_chart(df):
    st.subheader("감정 분포")

    counts = (
        df["sentiment_ui"]
        .value_counts()
        .reindex(["긍정", "중립", "부정"])
        .fillna(0)
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(counts.index, counts.values)

    ax.set_xlabel("감정", fontsize=14)
    ax.set_ylabel("댓글 수", fontsize=14)
    ax.set_title("댓글 감정 분포", fontsize=16)

    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()      # 🔥 글씨 잘림 방지

    st.pyplot(fig)


# ================================
# 3) 악성 댓글 분포 그래프
# ================================
def render_hate_chart(df):
    st.subheader("악성 댓글 분포")

    counts = df["is_hate"].value_counts().sort_index()

    if len(counts) == 2:
        counts.index = ["정상", "악성"]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(counts.index, counts.values)

    ax.set_xlabel("댓글 유형", fontsize=14)
    ax.set_ylabel("댓글 수", fontsize=14)
    ax.set_title("악성 댓글 비율 분포", fontsize=16)

    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()   # 🔥 글씨 겹침 방지

    st.pyplot(fig)


# ================================
# 4) 날짜별 여론 추이
# ================================
def render_trend_section(df: pd.DataFrame):
    # 날짜 정보 없으면 바로 종료
    if "date_for_trend" not in df.columns or "comment" not in df.columns:
        return

    tmp = df.dropna(subset=["date_for_trend"]).copy()
    if tmp.empty:
        return

    # 날짜별 댓글 수
    trend = (
        tmp.groupby("date_for_trend")
        .agg(n_comments=("comment", "count"))
        .sort_index()
    )

    # 날짜별 긍정 비율
    if "sentiment_ui" in tmp.columns:
        pos_series = (
            tmp.groupby("date_for_trend")["sentiment_ui"]
            .apply(lambda s: (s == "긍정").mean() * 100)
        )
        trend["pos_ratio"] = pos_series
    else:
        trend["pos_ratio"] = 0.0

    # 숫자형으로 강제 변환 (TypeError 방지)
    trend["n_comments"] = pd.to_numeric(trend["n_comments"], errors="coerce").fillna(0)
    trend["pos_ratio"] = pd.to_numeric(trend["pos_ratio"], errors="coerce").fillna(0)

    st.subheader("📅 날짜별 여론 추이")

    col1, col2 = st.columns(2)

    # 날짜별 댓글 수
    with col1:
        fig1, ax1 = plt.subplots()
        trend["n_comments"].plot(ax=ax1)
        ax1.set_xlabel("날짜")
        ax1.set_ylabel("댓글 수")
        ax1.set_title("날짜별 댓글 수 추이")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig1)

    # 날짜별 긍정 비율
    with col2:
        fig2, ax2 = plt.subplots()
        trend["pos_ratio"].plot(ax=ax2)
        ax2.set_xlabel("날짜")
        ax2.set_ylabel("긍정 비율(%)")
        ax2.set_title("날짜별 긍정 비율 추이")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig2)


# ================================
# 5) 워드클라우드 섹션
# ================================
def _build_wordcloud(text_series):
    """댓글 Series를 받아서 워드클라우드 figure 생성"""
    texts = [str(t) for t in text_series if isinstance(t, str)]
    joined = " ".join(texts)
    if not joined.strip():
        return None

    wc = WordCloud(
        width=800,
        height=400,
        background_color="white",
        font_path=FONT_PATH if FONT_PATH else None,
     ).generate(joined)


    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    return fig


def render_wordcloud_section(df: pd.DataFrame):
    st.subheader("☁ 키워드 분석 (워드클라우드)")

    # 기본 텍스트 컬럼 선택
    if "comment_clean" in df.columns:
        base_text = df["comment_clean"]
    elif "comment" in df.columns:
        base_text = df["comment"]
    else:
        st.info("댓글 텍스트 컬럼(comment / comment_clean)을 찾을 수 없습니다.")
        return

    # 전체 댓글 워드클라우드
    st.markdown("#### 🧾 전체 댓글 워드클라우드")
    fig_all = _build_wordcloud(base_text)
    if fig_all is not None:
        st.pyplot(fig_all)
    else:
        st.info("워드클라우드를 생성할 텍스트가 없습니다.")

    col_pos, col_neg = st.columns(2)

    # 긍정 댓글
    with col_pos:
        st.markdown("##### 🙂 긍정 댓글 키워드")
        if "sentiment_ui" in df.columns:
            pos_text = base_text[df["sentiment_ui"] == "긍정"]
            fig_pos = _build_wordcloud(pos_text)
            if fig_pos is not None:
                st.pyplot(fig_pos)
            else:
                st.info("긍정 댓글이 충분하지 않습니다.")
        else:
            st.info("감정 정보가 없어 긍정 댓글 워드클라우드를 만들 수 없습니다.")

    # 부정 댓글
    with col_neg:
        st.markdown("##### 🙁 부정 댓글 키워드")
        if "sentiment_ui" in df.columns:
            neg_text = base_text[df["sentiment_ui"] == "부정"]
            fig_neg = _build_wordcloud(neg_text)
            if fig_neg is not None:
                st.pyplot(fig_neg)
            else:
                st.info("부정 댓글이 충분하지 않습니다.")
        else:
            st.info("감정 정보가 없어 부정 댓글 워드클라우드를 만들 수 없습니다.")

    # 악성 댓글 워드클라우드
    if "is_hate" in df.columns:
        st.markdown("#### ⚠️ 악성 댓글 키워드")
        hate_text = base_text[df["is_hate"] == 1]
        fig_hate = _build_wordcloud(hate_text)
        if fig_hate is not None:
            st.pyplot(fig_hate)
        else:
            st.info("악성 댓글이 충분하지 않습니다.")
