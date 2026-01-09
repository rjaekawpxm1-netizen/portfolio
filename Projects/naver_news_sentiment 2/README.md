# 📰 Naver News Comment Sentiment Analysis
네이버 뉴스 댓글을 자동 크롤링하여 감정 분석과 텍스트 마이닝을 수행하고, Tableau로 시각화한 데이터 분석 프로젝트입니다.

<br>

## 📈 프로젝트 개요
이 프로젝트는 다음과 같은 흐름으로 구성되어 있습니다.

1. **네이버 뉴스 기사 URL 수집 (Selenium)**
2. **댓글 크롤링 (Selenium WebDriver)**
3. **텍스트 전처리 및 형태소 분석**
4. **감정 분석(긍정/중립/부정)**
5. **단어 빈도 분석 및 WordCloud 생성**
6. **Tableau를 활용한 최종 시각화 대시보드 제작**

> Python 기반 데이터 파이프라인 + Tableau 시각화가 결합된 End-to-End 프로젝트입니다.

<br>

---

## 🛠 기술 스택 (Tech Stack)

### **Language**
- Python 3.x

### **Libraries**
- Selenium
- BeautifulSoup4
- Transformers (HuggingFace)
- PyTorch
- Pandas / NumPy
- WordCloud
- KoNLPy / Okt
- Matplotlib

### **Visualization**
- Tableau Public

### **Tools**
- VSCode
- ChromeDriver
- Git / GitHub

<br>

---

## 📁 프로젝트 구조 (Project Structure)

```plaintext
project/
│
├── data/
│   ├── raw/
│   │   ├── news_urls.csv
│   │   ├── comments_selenium.csv
│   │
│   ├── processed/
│       ├── comments_with_sentiment.csv
│       ├── word_frequency.csv
│       ├── word_freq_긍정.csv
│       ├── word_freq_중립.csv
│       ├── word_freq_부정.csv
│       ├── wordcloud_*.png
│
├── src/
│   ├── crawl_news_urls.py
│   ├── naver_comment_selenium.py
│   ├── sentiment_analysis.py
│   ├── text_analysis.py
│   ├── run_all.py
│
├── tableau/
│   ├── dashboard.twbx  (Tableau 대시보드 파일)
│
└── README.md
