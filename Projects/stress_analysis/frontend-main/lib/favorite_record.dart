import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'my_page.dart';

class FavoriteRecordPage extends StatefulWidget {
  const FavoriteRecordPage({super.key});

  @override
  State<FavoriteRecordPage> createState() => _FavoriteRecordPageState();
}

class _FavoriteRecordPageState extends State<FavoriteRecordPage> {
  List<Map<String, dynamic>> favoriteRecords = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchFavoriteRecords();
  }

  Future<void> fetchFavoriteRecords() async {
    final prefs = await SharedPreferences.getInstance();
    String? email =
        prefs.getString('userEmail') ?? prefs.getString('loggedInUserEmail');

    if (email == null || email.isEmpty) {
      setState(() => isLoading = false);
      return;
    }

    final url =
    Uri.parse('http://10.0.2.2:8080/api/records/favorites?email=$email');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
      setState(() {
        favoriteRecords = data
            .map((item) => {
          "id": item["id"],
          "finalScore": item["finalScore"] ?? 0,
          "emotion": item["emotion"] ?? "Unknown",
          "createdAt": item["createdAt"],
          "recommendedSongs": item["recommendedSongs"] ?? "",
          "recommendedMovie": item["recommendedMovie"] ?? "",
          "moviePosterUrl": item["moviePosterUrl"] ?? "",
          "movieRatingPercent": item["movieRatingPercent"] ?? 0,
          "solution": item["solution"] ?? item["reason"] ?? "",
          "favorite": item["favorite"] ?? false,
        })
            .toList();
        favoriteRecords.sort((a, b) =>
            b["createdAt"].toString().compareTo(a["createdAt"].toString()));
        isLoading = false;
      });
    } else {
      setState(() => isLoading = false);
    }
  }

  Future<void> deleteRecord(int recordId) async {
    final url = Uri.parse("http://10.0.2.2:8080/api/records/$recordId");
    try {
      final response = await http.delete(url);
      if (response.statusCode == 200) {
        setState(() {
          favoriteRecords.removeWhere((r) => r["id"] == recordId);
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("기록이 삭제되었습니다.")),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("삭제 중 오류 발생: $e")),
      );
    }
  }

  Future<void> toggleFavorite(int recordId, bool currentFavorite) async {
    final url =
    Uri.parse("http://10.0.2.2:8080/api/records/$recordId/favorite");
    try {
      final response = await http.patch(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"favorite": !currentFavorite}),
      );
      if (response.statusCode == 200) {
        await fetchFavoriteRecords();
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
    final color = _getLevelColor(record["emotion"]);
    final emotionLabel = _getEmotionLabel(record["emotion"]);

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
                children: [
                  // 상단 점수 & 즐겨찾기
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

                  // 말풍선
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.chat_bubble_outline, color: Colors.grey),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            (record["solution"] ?? "").isNotEmpty
                                ? record["solution"]
                                : "당신의 감정은 소중합니다. 잠시 쉬어가세요.",
                            style: const TextStyle(
                              fontSize: 16,
                              color: Colors.black87,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 25),

                  // 추천 노래
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
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: (record["recommendedSongs"] ?? "")
                          .toString()
                          .split('\n')
                          .where((s) => s.trim().isNotEmpty)
                          .map((s) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          children: [
                            const Icon(Icons.music_note,
                                size: 18, color: Colors.black54),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                s,
                                style: const TextStyle(fontSize: 15),
                              ),
                            ),
                          ],
                        ),
                      ))
                          .toList(),
                    ),
                  ),

                  const SizedBox(height: 25),

                  // 추천 영화
                  if ((record["recommendedMovie"] ?? "").isNotEmpty) ...[
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
                          if ((record["moviePosterUrl"] ?? "").isNotEmpty)
                            ClipRRect(
                              borderRadius: BorderRadius.circular(12),
                              child: Image.network(
                                record["moviePosterUrl"],
                                height: 220,
                                fit: BoxFit.cover,
                                errorBuilder: (_, __, ___) => const Icon(
                                  Icons.broken_image,
                                  size: 100,
                                  color: Colors.grey,
                                ),
                              ),
                            ),
                          const SizedBox(height: 10),
                          Text(
                            record["recommendedMovie"],
                            style: const TextStyle(
                              fontSize: 17,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          if (record["movieRatingPercent"] != null)
                            Text(
                              "평점: ${record["movieRatingPercent"]}%",
                              style: const TextStyle(fontSize: 15),
                            ),
                        ],
                      ),
                    ),
                  ],

                  const SizedBox(height: 30),

                  // 버튼들
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      ElevatedButton(
                        onPressed: () => Navigator.pop(context),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.grey[700],
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                        child: const Text('닫기'),
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
                                            fontWeight: FontWeight.bold),
                                      ),
                                      const SizedBox(height: 10),
                                      const Text(
                                        '이 기록은 내 기록에서도 함께 삭제됩니다.\n정말 삭제하시겠습니까?',
                                        textAlign: TextAlign.center,
                                        style: TextStyle(
                                            fontSize: 15, color: Colors.black54),
                                      ),
                                      const SizedBox(height: 20),
                                      Row(
                                        children: [
                                          Expanded(
                                            child: ElevatedButton(
                                              onPressed: () =>
                                                  Navigator.pop(context, false),
                                              style: ElevatedButton.styleFrom(
                                                backgroundColor:
                                                Colors.grey[300],
                                                foregroundColor: Colors.black87,
                                                shape: RoundedRectangleBorder(
                                                  borderRadius:
                                                  BorderRadius.circular(12),
                                                ),
                                              ),
                                              child: const Text('취소'),
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
                                              ),
                                              child: const Text('삭제'),
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
                            Navigator.pop(context);
                          }
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10)),
                        ),
                        child:
                        const Text('지우기', style: TextStyle(fontWeight: FontWeight.bold)),
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
    return WillPopScope(
      onWillPop: () async {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const MyPage()),
        );
        return false;
      },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: const Color(0xFF3B82F6),
          centerTitle: true,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back, color: Colors.white),
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const MyPage()),
              );
            },
          ),
          title: const Text('⭐ 즐겨찾기 기록',
              style: TextStyle(color: Colors.white)),
        ),
        body: isLoading
            ? const Center(child: CircularProgressIndicator())
            : favoriteRecords.isEmpty
            ? const Center(
            child: Text('📭 즐겨찾기된 기록이 없습니다.',
                style: TextStyle(fontSize: 18)))
            : ListView.builder(
          padding: const EdgeInsets.all(12),
          itemCount: favoriteRecords.length,
          itemBuilder: (context, index) {
            final record = favoriteRecords[index];
            final color = _getLevelColor(record["emotion"]);
            final emotionLabel =
            _getEmotionLabel(record["emotion"]);

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
                      const Icon(Icons.star, color: Colors.amber),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment:
                          CrossAxisAlignment.start,
                          children: [
                            Text(
                              '📜 ${index + 1}번째 즐겨찾기',
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
      ),
    );
  }
}
