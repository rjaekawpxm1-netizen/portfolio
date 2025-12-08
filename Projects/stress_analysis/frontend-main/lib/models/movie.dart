class Movie {
  final String title;
  final String posterUrl;
  final String overview;
  final int voteCount;
  final double popularity;
  final double voteAverage; // ⭐ 평점 추가 (0~10)

  Movie({
    required this.title,
    required this.posterUrl,
    required this.overview,
    required this.voteCount,
    required this.popularity,
    required this.voteAverage,
  });

  factory Movie.fromJson(Map<String, dynamic> json) {
    return Movie(
      title: json['title'] ?? '',
      posterUrl: json['posterUrl'] ?? '',
      overview: json['overview'] ?? '',
      voteCount: json['vote_count'] ?? 0,
      popularity: (json['popularity'] ?? 0).toDouble(),
      voteAverage: (json['vote_average'] ?? 0).toDouble(), // ⭐ 추가
    );
  }
}
