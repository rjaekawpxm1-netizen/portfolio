import 'package:flutter/material.dart';
import 'home_page.dart';
import 'package:camera/camera.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ResultScreen extends StatefulWidget {
  final List<CameraDescription> cameras;

  const ResultScreen({super.key, required this.cameras});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  double? finalScore;
  String? recommendedSongs;
  String? emotion;
  String? movieTitle;
  String? moviePosterUrl;
  int? movieRating;
  String? solution;

  @override
  void initState() {
    super.initState();
    fetchFinalScore();
  }

  String getEmotionLabel(String? emotion) {
    switch (emotion) {
      case "Anger":
        return "분노";
      case "Anxiety":
        return "불안";
      case "Sadness":
        return "우울";
      case "Normal":
        return "양호";
      default:
        return "알 수 없음";
    }
  }

  Color getEmotionColor(String? emotion) {
    switch (emotion) {
      case "Anger":
        return Colors.redAccent;
      case "Anxiety":
        return Colors.orangeAccent;
      case "Sadness":
        return Colors.indigoAccent;
      case "Normal":
        return Colors.green;
      default:
        return Colors.blueGrey;
    }
  }

  Future<void> fetchFinalScore() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      int? scoreId = prefs.getInt('currentScoreId');

      var url = Uri.parse("http://10.0.2.2:8080/api/final/get?scoreId=$scoreId");
      var response = await http.get(url);

      if (response.statusCode == 200) {
        var data = jsonDecode(response.body);

        setState(() {
          finalScore = (data['finalScore'] ?? 0).toDouble();
          recommendedSongs = data['recommendedSongs'] ?? "추천 곡 없음";
          emotion = data['emotion'] ?? "Unknown";
          movieTitle = data['recommendedMovie'] ?? "추천 영화 없음";
          moviePosterUrl = data['moviePosterUrl'];
          movieRating = data['movieRatingPercent'];
          solution = data['solution'] ?? "";
        });
      } else {
        print("❌ 점수 불러오기 실패: ${response.statusCode}");
      }
    } catch (e) {
      print("⚠️ 에러 발생: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = getEmotionColor(emotion);
    final label = getEmotionLabel(emotion);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: color,
        elevation: 0,
        centerTitle: true,
        title: const Text(
          '검사 결과',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFF9FAFB), Color(0xFFE0ECFF)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 30),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // 🧠 감정 요약 카드
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: color.withOpacity(0.4), width: 1.2),
                ),
                child: Column(
                  children: [
                    Icon(
                      emotion == "Normal"
                          ? Icons.sentiment_satisfied_alt_rounded
                          : emotion == "Sadness"
                          ? Icons.sentiment_dissatisfied_rounded
                          : emotion == "Anxiety"
                          ? Icons.sentiment_neutral_rounded
                          : Icons.sentiment_very_dissatisfied_rounded,
                      size: 60,
                      color: color,
                    ),
                    const SizedBox(height: 10),
                    Text(
                      label,
                      style: TextStyle(
                          fontSize: 22, fontWeight: FontWeight.bold, color: color),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      finalScore != null
                          ? "스트레스 점수: ${finalScore!.toStringAsFixed(0)}점"
                          : "로딩중...",
                      style: const TextStyle(fontSize: 18, color: Colors.black87),
                    ),
                    const SizedBox(height: 20),
                    AnimatedOpacity(
                      opacity: (solution != null && solution!.isNotEmpty) ? 1.0 : 0.4,
                      duration: const Duration(milliseconds: 600),
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: color.withOpacity(0.5)),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.grey.withOpacity(0.2),
                              blurRadius: 6,
                              offset: const Offset(0, 3),
                            ),
                          ],
                        ),
                        child: Text(
                          solution ?? "해결방안 정보를 불러오는 중...",
                          textAlign: TextAlign.center,
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 30),

              // 🎧 추천 노래
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: color.withOpacity(0.3)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black12.withOpacity(0.05),
                      blurRadius: 6,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('🎵 AI 추천 노래',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 10),
                    if (recommendedSongs != null)
                      ...recommendedSongs!
                          .split(RegExp(r'\\n|\n'))
                          .where((song) => song.trim().isNotEmpty)
                          .map((song) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Text(
                          "🎧 $song",
                          style: const TextStyle(fontSize: 16, color: Colors.black87),
                        ),
                      ))
                          .toList()
                    else
                      const Text("추천 곡 로딩중...", style: TextStyle(fontSize: 16)),
                  ],
                ),
              ),

              const SizedBox(height: 30),

              // 🎬 추천 영화
              if (movieTitle != null && movieTitle != "추천 영화 없음")
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: color.withOpacity(0.3)),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black12.withOpacity(0.08),
                        blurRadius: 6,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      const Text("🎬 AI 추천 영화",
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 10),
                      if (moviePosterUrl != null && moviePosterUrl!.isNotEmpty)
                        ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: Image.network(
                            moviePosterUrl!,
                            height: 250,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) =>
                            const Icon(Icons.broken_image, size: 100, color: Colors.grey),
                          ),
                        ),
                      const SizedBox(height: 10),
                      Text(movieTitle!,
                          style: const TextStyle(
                              fontSize: 18, fontWeight: FontWeight.bold, color: Colors.black87)),
                      if (movieRating != null) ...[
                        const SizedBox(height: 6),
                        LinearProgressIndicator(
                          value: movieRating! / 100,
                          color: color,
                          backgroundColor: Colors.grey[300],
                          minHeight: 6,
                        ),
                        const SizedBox(height: 4),
                        Text("평점: ${movieRating!}%",
                            style: const TextStyle(fontSize: 14, color: Colors.black54)),
                      ],
                    ],
                  ),
                ),

              const SizedBox(height: 40),

              // 완료 버튼 (그라데이션)
              Container(
                width: double.infinity,
                height: 50,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  gradient: const LinearGradient(
                    colors: [Color(0xFF3B82F6), Color(0xFF60A5FA)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushAndRemoveUntil(
                      context,
                      MaterialPageRoute(
                          builder: (context) =>
                              HomePage(cameras: [widget.cameras.first])),
                          (route) => false,
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Text(
                    '완료',
                    style: TextStyle(
                        fontSize: 18, color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
