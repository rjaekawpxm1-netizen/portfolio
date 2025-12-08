import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/movie.dart';
import '../services/recommendation_api.dart';

class EmotionMovieList extends StatefulWidget {
  final String emotion;

  const EmotionMovieList({super.key, required this.emotion});

  @override
  State<EmotionMovieList> createState() => _EmotionMovieListState();
}

class _EmotionMovieListState extends State<EmotionMovieList> {
  late Future<List<Movie>> future;

  @override
  void initState() {
    super.initState();
    future = RecommendationApi().fetchMoviesByEmotion(widget.emotion);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Movie>>(
      future: future,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        } else if (snapshot.hasError) {
          return Text("오류 발생: ${snapshot.error}");
        } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
          return const Text("추천 영화가 없습니다.");
        }

        final movies = snapshot.data!;

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "🎬 감정 기반 추천 영화",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 15),

            SizedBox(
              height: 340,
              child: PageView.builder(
                itemCount: movies.length,
                controller: PageController(viewportFraction: 0.8),
                itemBuilder: (context, index) {
                  final movie = movies[index];

                  final description = (movie.overview.isNotEmpty &&
                      movie.overview.toLowerCase() != "null")
                      ? movie.overview
                      : "🎬 해당 영화에 대한 상세 정보가 부족합니다.";

                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8.0),
                    child: GestureDetector(
                      onTap: () {
                        // ✅ 상세 팝업 띄우기
                        showDialog(
                          context: context,
                          builder: (context) {
                            return Dialog(
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(16),
                              ),
                              insetPadding: const EdgeInsets.all(20),
                              child: SizedBox(
                                height: 520,
                                child: Padding(
                                  padding: const EdgeInsets.all(16.0),
                                  child: Stack(
                                    children: [
                                      SingleChildScrollView(
                                        child: Column(
                                          crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                          children: [
                                            // 포스터 이미지
                                            ClipRRect(
                                              borderRadius:
                                              BorderRadius.circular(12),
                                              child: CachedNetworkImage(
                                                imageUrl: movie.posterUrl,
                                                height: 260,
                                                width: double.infinity,
                                                fit: BoxFit.contain, // 🔹 비율 유지
                                                errorWidget: (context, url,
                                                    error) =>
                                                const Icon(
                                                    Icons.image_not_supported,
                                                    size: 48),
                                              ),
                                            ),
                                            const SizedBox(height: 16),
                                            Text(
                                              movie.title.isNotEmpty
                                                  ? movie.title
                                                  : "제목 정보 없음",
                                              style: const TextStyle(
                                                fontSize: 20,
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                            const SizedBox(height: 8),
                                            // 🔹 평점 표시 (퍼센트)
                                            Text(
                                              "평점: ${(movie.voteAverage * 10).round()}%",
                                              style: const TextStyle(
                                                fontSize: 16,
                                                fontWeight: FontWeight.w600,
                                                color: Colors.orange,
                                              ),
                                            ),
                                            const SizedBox(height: 12),
                                            Text(
                                              description,
                                              style: const TextStyle(
                                                fontSize: 16,
                                                height: 1.4,
                                              ),
                                            ),
                                            const SizedBox(height: 20),
                                          ],
                                        ),
                                      ),

                                      // 닫기 버튼
                                      Positioned(
                                        top: 0,
                                        right: 0,
                                        child: IconButton(
                                          icon: const Icon(Icons.close),
                                          onPressed: () =>
                                              Navigator.of(context).pop(),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            );
                          },
                        );
                      },
                      child: Card(
                        elevation: 4,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // ✅ 포스터 이미지
                            ClipRRect(
                              borderRadius: const BorderRadius.vertical(
                                  top: Radius.circular(16)),
                              child: CachedNetworkImage(
                                imageUrl: movie.posterUrl,
                                height: 200,
                                width: double.infinity,
                                fit: BoxFit.contain, // 🔹 이미지 잘림 방지
                                placeholder: (context, url) => const Center(
                                  child: CircularProgressIndicator(),
                                ),
                                errorWidget: (context, url, error) =>
                                const Center(child: Icon(Icons.error)),
                              ),
                            ),

                            // ✅ 영화 제목 + 간략 설명
                            Expanded(
                              child: Padding(
                                padding: const EdgeInsets.all(12.0),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      movie.title.isNotEmpty
                                          ? movie.title
                                          : "제목 정보가 없습니다.",
                                      style: const TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      "평점: ${(movie.voteAverage * 10).round()}%",
                                      style: const TextStyle(
                                        fontSize: 14,
                                        fontWeight: FontWeight.w500,
                                        color: Colors.orange,
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    Flexible(
                                      child: Text(
                                        description,
                                        maxLines: 3,
                                        overflow: TextOverflow.ellipsis,
                                        style:
                                        const TextStyle(fontSize: 14, height: 1.3),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }
}
