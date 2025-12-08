import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'my_page.dart';

class MyRecordPage extends StatefulWidget {
  const MyRecordPage({super.key});

  @override
  _MyRecordPageState createState() => _MyRecordPageState();
}

class _MyRecordPageState extends State<MyRecordPage> {
  List<Map<String, dynamic>> records = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchRecordsFromServer();
  }

  Future<void> fetchRecordsFromServer() async {
    final prefs = await SharedPreferences.getInstance();
    String? email =
        prefs.getString('userEmail') ?? prefs.getString('loggedInUserEmail');
    if (email == null || email.isEmpty) {
      setState(() => isLoading = false);
      return;
    }

    final url = Uri.parse('http://10.0.2.2:8080/api/records?email=$email');
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        setState(() {
          records = data.map((item) => item as Map<String, dynamic>).toList();
          records.sort((a, b) =>
              b["createdAt"].toString().compareTo(a["createdAt"].toString()));
          isLoading = false;
        });
      } else {
        setState(() => isLoading = false);
      }
    } catch (e) {
      setState(() => isLoading = false);
    }
  }

  Future<void> deleteRecord(int recordId) async {
    final url = Uri.parse("http://10.0.2.2:8080/api/records/$recordId");
    try {
      final response = await http.delete(url);
      if (response.statusCode == 200) {
        await fetchRecordsFromServer();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text("기록이 삭제되었습니다.")),
          );
        }
      }
    } catch (_) {}
  }

  Future<void> toggleFavorite(int recordId, bool currentFavorite) async {
    final url =
    Uri.parse("http://10.0.2.2:8080/api/records/$recordId/favorite");
    try {
      final response = await http.patch(
        url,
        headers: {"Content-Type": "application/json"},
        body: json.encode({"favorite": !currentFavorite}),
      );
      if (response.statusCode == 200) {
        await fetchRecordsFromServer();
      }
    } catch (_) {}
  }

  String _getEmotionLabel(String? emotion) {
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

  Color _getLevelColor(String emotion) {
    switch (emotion) {
      case "Anger":
        return Colors.redAccent;
      case "Anxiety":
        return Colors.orangeAccent;
      case "Sadness":
        return const Color(0xFF3B82F6);
      case "Normal":
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  void _showRecordDetail(BuildContext context, Map<String, dynamic> record) {
    final moviePosterUrl =
        record["moviePosterUrl"] ?? record["movie_poster_url"];
    final recommendedMovie =
        record["recommendedMovie"] ?? record["recommended_movie"];
    final movieRatingPercent =
        record["movieRatingPercent"] ?? record["movie_rating_percent"];
    final emotion = record["emotion"];
    final color = _getLevelColor(emotion);
    final emotionLabel = _getEmotionLabel(emotion);

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return Dialog(
          backgroundColor: Colors.transparent,
          insetPadding: const EdgeInsets.all(16),
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: color.withOpacity(0.3),
                  blurRadius: 12,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // 상단 점수 / 즐겨찾기
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      IconButton(
                        icon: Icon(
                          record["favorite"]
                              ? Icons.star
                              : Icons.star_border_outlined,
                          color: record["favorite"]
                              ? Colors.yellow[700]
                              : Colors.grey,
                        ),
                        onPressed: () async {
                          await toggleFavorite(record["id"], record["favorite"]);
                          Navigator.of(context).pop();
                        },
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '스트레스 점수: ${record["finalScore"]}',
                        style: TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: color,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    emotionLabel,
                    style: TextStyle(
                      fontSize: 18,
                      color: color,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 20),

                  // 말풍선 영역
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.chat_bubble_outline,
                            color: Colors.grey),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            record["solution"]?.toString().isNotEmpty == true
                                ? record["solution"]
                                : "감정을 억누르지 말고 느껴보세요. 그것도 치유의 시작이에요.",
                            style: const TextStyle(
                                fontSize: 16, color: Colors.black87),
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 25),

                  // AI 추천 노래
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      '🎵추천 노래',
                      style: TextStyle(
                        fontSize: 18,
                        color: color,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.grey[100],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: (record["recommendedSongs"]?.toString() ?? '')
                          .split('\n')
                          .where((s) => s.trim().isNotEmpty)
                          .map((s) => Padding(
                        padding:
                        const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          children: [
                            const Icon(Icons.music_note,
                                size: 18, color: Colors.black54),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                s,
                                style: const TextStyle(
                                    fontSize: 15,
                                    color: Colors.black87),
                              ),
                            ),
                          ],
                        ),
                      ))
                          .toList(),
                    ),
                  ),

                  const SizedBox(height: 25),

                  // AI 추천 영화
                  if (recommendedMovie != null &&
                      (recommendedMovie as String).isNotEmpty) ...[
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        '🎬추천 영화',
                        style: TextStyle(
                          fontSize: 18,
                          color: color,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.grey[100],
                        borderRadius: BorderRadius.circular(12),
                      ),
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        children: [
                          if (moviePosterUrl != null &&
                              (moviePosterUrl as String).isNotEmpty)
                            ClipRRect(
                              borderRadius: BorderRadius.circular(12),
                              child: Image.network(
                                moviePosterUrl,
                                height: 220,
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) =>
                                const Icon(Icons.broken_image,
                                    size: 100, color: Colors.grey),
                              ),
                            ),
                          const SizedBox(height: 10),
                          Text(
                            recommendedMovie,
                            style: const TextStyle(
                                fontSize: 17, fontWeight: FontWeight.w600),
                            textAlign: TextAlign.center,
                          ),
                          if (movieRatingPercent != null)
                            Text("평점: $movieRatingPercent%",
                                style: const TextStyle(fontSize: 15)),
                        ],
                      ),
                    ),
                  ],

                  const SizedBox(height: 30),

                  // 닫기 / 삭제 버튼
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      ElevatedButton(
                        onPressed: () => Navigator.of(context).pop(),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.grey[700],
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10)),
                        ),
                        child: const Text('닫기',
                            style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                      const SizedBox(width: 16),
                      ElevatedButton(
                        onPressed: () async {
                          final confirmed = await showDialog<bool>(
                            context: context,
                            barrierDismissible: false,
                            builder: (context) {
                              return Dialog(
                                backgroundColor: Colors.white,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(20),
                                ),
                                child: Padding(
                                  padding: const EdgeInsets.all(24.0),
                                  child: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(Icons.warning_amber_rounded,
                                          color: color, size: 48),
                                      const SizedBox(height: 12),
                                      const Text(
                                        '기록 삭제',
                                        style: TextStyle(
                                            fontSize: 20,
                                            fontWeight: FontWeight.bold,
                                            color: Colors.black87),
                                      ),
                                      const SizedBox(height: 10),
                                      const Text(
                                        '삭제된 기록은 복원이 불가능합니다.\n정말 삭제하시겠습니까?',
                                        textAlign: TextAlign.center,
                                        style: TextStyle(
                                            fontSize: 15,
                                            color: Colors.black54),
                                      ),
                                      const SizedBox(height: 20),
                                      Row(
                                        mainAxisAlignment:
                                        MainAxisAlignment.center,
                                        children: [
                                          Expanded(
                                            child: ElevatedButton(
                                              onPressed: () =>
                                                  Navigator.pop(context, false),
                                              style: ElevatedButton.styleFrom(
                                                backgroundColor:
                                                Colors.grey[300],
                                                foregroundColor:
                                                Colors.black87,
                                                shape: RoundedRectangleBorder(
                                                  borderRadius:
                                                  BorderRadius.circular(12),
                                                ),
                                                padding:
                                                const EdgeInsets.symmetric(
                                                    vertical: 12),
                                              ),
                                              child: const Text('취소',
                                                  style: TextStyle(
                                                      fontWeight:
                                                      FontWeight.bold)),
                                            ),
                                          ),
                                          const SizedBox(width: 16),
                                          Expanded(
                                            child: ElevatedButton(
                                              onPressed: () =>
                                                  Navigator.pop(context, true),
                                              style: ElevatedButton.styleFrom(
                                                backgroundColor: color,
                                                foregroundColor: Colors.white,
                                                shape: RoundedRectangleBorder(
                                                  borderRadius:
                                                  BorderRadius.circular(12),
                                                ),
                                                padding:
                                                const EdgeInsets.symmetric(
                                                    vertical: 12),
                                              ),
                                              child: const Text('삭제',
                                                  style: TextStyle(
                                                      fontWeight:
                                                      FontWeight.bold)),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            },
                          );

                          if (confirmed == true) {
                            await deleteRecord(record["id"]);
                            Navigator.of(context).pop();
                          }
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10)),
                        ),
                        child: const Text('지우기',
                            style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF3B82F6),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () {
            Navigator.pushReplacement(
                context, MaterialPageRoute(builder: (context) => const MyPage()));
          },
        ),
        centerTitle: true,
        title: const Text('📜 내 기록', style: TextStyle(color: Colors.white)),
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : records.isEmpty
          ? const Center(
          child: Text("📭 저장된 기록이 없습니다.",
              style: TextStyle(fontSize: 18)))
          : ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: records.length,
        itemBuilder: (context, index) {
          final record = records[index];
          final emotionLabel = _getEmotionLabel(record["emotion"]);
          final color = _getLevelColor(record["emotion"]);

          return GestureDetector(
            onTap: () => _showRecordDetail(context, record),
            child: Card(
              elevation: 3,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              margin: const EdgeInsets.symmetric(vertical: 8),
              child: Container(
                decoration: BoxDecoration(
                  border: Border(
                    left: BorderSide(color: color, width: 6),
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                padding: const EdgeInsets.symmetric(
                    vertical: 16, horizontal: 20),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment:
                        CrossAxisAlignment.start,
                        children: [
                          Text(
                            '📜 ${index + 1}번째 기록',
                            style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '점수: ${record["finalScore"]}   감정: $emotionLabel',
                            style: TextStyle(
                              fontSize: 15,
                              color: color,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '날짜: ${record["createdAt"].toString().substring(0, 10)}',
                            style: const TextStyle(
                                color: Colors.black54),
                          ),
                        ],
                      ),
                    ),
                    const Icon(Icons.chevron_right,
                        color: Colors.grey),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
