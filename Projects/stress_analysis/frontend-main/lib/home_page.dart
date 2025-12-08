import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:animated_text_kit/animated_text_kit.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'camera_screen.dart';
import 'my_page.dart';
import 'relax_page.dart';

class HomePage extends StatefulWidget {
  final List<CameraDescription> cameras;

  const HomePage({super.key, required this.cameras});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  Map<String, dynamic>? latestRecord;
  bool isLoading = true;

  Future<void> createNewSession() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final email = prefs.getString('loggedInUserEmail') ?? '';

      if (email.isEmpty) return;

      var url = Uri.parse("http://10.0.2.2:8080/api/scores/init");
      var response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );

      if (response.statusCode == 200) {
        int id = int.parse(response.body);
        prefs.setInt('currentScoreId', id);
        print("✅ 새로운 세션 생성됨: id = $id");
      }
    } catch (e) {
      print("에러 발생: $e");
    }
  }

  Future<void> fetchLatestRecord() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final email = prefs.getString('loggedInUserEmail') ?? '';

      if (email.isEmpty) {
        setState(() => isLoading = false);
        return;
      }

      final url =
      Uri.parse("http://10.0.2.2:8080/api/records/latest?email=$email");
      final response = await http.get(url);

      if (!mounted) return;

      if (response.statusCode == 200 && response.body.isNotEmpty) {
        final decoded = jsonDecode(utf8.decode(response.bodyBytes));
        if (decoded is Map<String, dynamic> && decoded.isNotEmpty) {
          setState(() {
            latestRecord = decoded;
            isLoading = false;
          });
        } else {
          setState(() {
            latestRecord = null;
            isLoading = false;
          });
        }
      } else {
        setState(() {
          latestRecord = null;
          isLoading = false;
        });
      }
    } catch (e) {
      print("에러 발생: $e");
      if (mounted) {
        setState(() {
          latestRecord = null;
          isLoading = false;
        });
      }
    }
  }

  String extractFirstSong(String? songs) {
    if (songs == null || songs.trim().isEmpty) return "없음";
    final parts = songs.trim().split('\n');
    return parts.isNotEmpty && parts.first.trim().isNotEmpty
        ? parts.first.trim()
        : "없음";
  }

  @override
  void initState() {
    super.initState();
    fetchLatestRecord();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F6FB),
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor: const Color(0xFF3B82F6),
        elevation: 0,
        centerTitle: true,
        title: SizedBox(
          height: 30,
          child: DefaultTextStyle(
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w700,
              color: Colors.white,
            ),
            child: AnimatedTextKit(
              repeatForever: true,
              pause: const Duration(seconds: 2),
              animatedTexts: [
                FadeAnimatedText('오늘 나의 스트레스 상태는?',
                    duration: Duration(seconds: 5),
                    fadeInEnd: 0.2,
                    fadeOutBegin: 0.8),
                FadeAnimatedText('지금 당신의 감정은 어떤가요?',
                    duration: Duration(seconds: 5),
                    fadeInEnd: 0.2,
                    fadeOutBegin: 0.8),
                FadeAnimatedText('AI가 당신의 하루를 분석합니다.',
                    duration: Duration(seconds: 5),
                    fadeInEnd: 0.2,
                    fadeOutBegin: 0.8),
              ],
            ),
          ),
        ),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: SingleChildScrollView(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text(
                  '얼굴과 목소리를 기반으로\n감정 상태를 분석해보세요.',
                  textAlign: TextAlign.center,
                  style:
                  TextStyle(fontSize: 16, color: Colors.black54, height: 1.5),
                ),
                const SizedBox(height: 50),

                // 🔹 검사하기 버튼
                GestureDetector(
                  onTap: () async {
                    await createNewSession();
                    if (mounted) {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) =>
                              CameraScreen(cameras: widget.cameras),
                        ),
                      );
                    }
                  },
                  child: Container(
                    width: 160,
                    height: 160,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF60A5FA), Color(0xFF2563EB)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(25),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.blue.withOpacity(0.25),
                          blurRadius: 10,
                          offset: const Offset(0, 5),
                        ),
                      ],
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: const [
                        Icon(Icons.camera_alt, size: 65, color: Colors.white),
                        SizedBox(height: 12),
                        Text(
                          '검사하기',
                          style: TextStyle(
                            fontSize: 19,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 50),
                const Divider(thickness: 1.2, indent: 40, endIndent: 40),
                const SizedBox(height: 20),

                // 🔹 최근 검사 결과 (오류 방지 완료)
                isLoading
                    ? const CircularProgressIndicator(color: Colors.blueAccent)
                    : (latestRecord != null && latestRecord!.isNotEmpty)
                    ? Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black12,
                        blurRadius: 8,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '📊 최근 검사 결과',
                        style: TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF2563EB),
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                          '감정: ${latestRecord?["emotion"] ?? "데이터 없음"}'),
                      Text(
                          '점수: ${latestRecord?["finalScore"]?.toString() ?? "-"}'),
                      Text(
                          '추천 노래: ${extractFirstSong(latestRecord?["recommendedSongs"])}'),
                      Text(
                          '추천 영화: ${latestRecord?["recommendedMovie"] ?? "-"}'),
                    ],
                  ),
                )
                    : const Text(
                  '최근 검사 기록이 없습니다.',
                  style: TextStyle(
                      fontSize: 15, color: Colors.black54),
                ),
              ],
            ),
          ),
        ),
      ),

      // 🔹 하단 네비게이션: 홈 / 마이페이지 / 스트레스 해소
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: Colors.white,
        selectedItemColor: const Color(0xFF3B82F6),
        unselectedItemColor: Colors.grey,
        selectedLabelStyle: const TextStyle(fontWeight: FontWeight.bold),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: '홈',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: '마이페이지',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.spa),
            label: '스트레스 해소',
          ),
        ],
        onTap: (index) {
          if (index == 1) {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const MyPage()),
            );
          } else if (index == 2) {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const RelaxPage()),
            );
          }
        },
      ),
    );
  }
}
