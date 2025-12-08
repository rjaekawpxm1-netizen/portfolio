import sys
import pandas as pd
import random
import io
import requests


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


TMDB_API_KEY = "6f0ef6fcee2028e0ae134c40f141f4f7"


GENRE_MAP = {
    "Anger": "28",       # Action
    "Sadness": "18",     # Drama
    "Anxiety": "53",     # Thriller
    "Normal": "10751"    # Family
}


def recommend_songs(emotion):
    df = pd.read_csv("C:/Users/Huni/Desktop/Cap/UnifiedBackend/scripts/emotions_labeled.csv")
    df = df[df["emotion"] == emotion]

    if df.empty:
        return "해당 감정의 노래가 없습니다."

    sampled = df.sample(n=min(3, len(df)))
    results = [f"{row['name'].strip()} - {row['artists'].strip()}" for _, row in sampled.iterrows()]
    return "\n".join(results)


def recommend_movie(emotion):
    try:
        genre_id = GENRE_MAP.get(emotion, "18")
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=ko-KR&with_genres={genre_id}&sort_by=popularity.desc"
        response = requests.get(url)
        data = response.json()

        if "results" not in data or len(data["results"]) == 0:
            return ("추천 영화 없음", "", 0)

        movie = random.choice(data["results"])
        title = movie.get("title", "제목 없음")
        poster_path = movie.get("poster_path")
        poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
        rating = int(movie.get("vote_average", 0) * 10)

        return (title, poster, rating)
    except Exception:
        return ("영화 추천 실패", "", 0)

# ✅ 실행부
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("⚠️ 감정 인자 하나를 전달해야 합니다.")
        sys.exit(1)

    emotion = sys.argv[1]

    # ✅ 노래
    songs = recommend_songs(emotion)
    # ✅ 영화
    movie_title, poster_url, rating_percent = recommend_movie(emotion)

    
    songs = songs.replace("\n", "\\n")

    
    print(songs)           # ① recommended_songs
    print(movie_title)     # ② recommended_movie
    print(poster_url)      # ③ movie_poster_url
    print(rating_percent)  # ④ movie_rating_percent
