import 'dart:math';
import 'package:flutter/material.dart';
import 'questions.dart';
import 'result_screen.dart';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class QuestionScreen extends StatefulWidget {
  final List<CameraDescription> cameras;

  const QuestionScreen({super.key, required this.cameras});

  @override
  State<QuestionScreen> createState() => _QuestionScreenState();
}

class _QuestionScreenState extends State<QuestionScreen> {
  List<String> selectedQuestions = [];
  Map<int, String> answers = {};

  @override
  void initState() {
    super.initState();
    selectedQuestions = List.from(allQuestions)..shuffle(Random());
    selectedQuestions = selectedQuestions.take(5).toList();
  }

  void _updateAnswer(int index, String value) {
    setState(() {
      answers[index] = value;
    });
  }

  int calculateScore() {
    int totalScore = 0;
    answers.forEach((index, answer) {
      if (answer == '예') totalScore += 20;
    });
    return totalScore;
  }

  @override
  Widget build(BuildContext context) {
    bool isAllAnswered = answers.length == selectedQuestions.length;

    return Scaffold(
      backgroundColor: const Color(0xfff8f9fa),
      appBar: AppBar(
        backgroundColor: const Color(0xFF3B82F6),
        elevation: 1,
        title: const Text(
          '스트레스 진단',
          style: TextStyle(color: Colors.white),
        ),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Center(
              child: Column(
                children: [
                  Icon(Icons.self_improvement_rounded,
                      color: Color(0xFF3B82F6), size: 60),
                  SizedBox(height: 8),
                  Text(
                    "아래 문항에 솔직하게 답해주세요.",
                    style: TextStyle(
                        fontSize: 16,
                        color: Colors.black87,
                        fontWeight: FontWeight.w500),
                  ),
                  SizedBox(height: 10),
                ],
              ),
            ),
            const Divider(thickness: 1, color: Colors.grey, height: 30),
            const SizedBox(height: 10),

            // 질문 카드 리스트
            ...selectedQuestions.asMap().entries.map((entry) {
              int index = entry.key;
              String question = entry.value;

              return Container(
                margin: const EdgeInsets.only(bottom: 20),
                padding:
                const EdgeInsets.symmetric(vertical: 18, horizontal: 16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.withOpacity(0.15),
                      blurRadius: 6,
                      offset: const Offset(0, 4),
                    ),
                  ],
                  border:
                  Border.all(color: Colors.blueAccent.withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${index + 1}. $question',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.black87,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        ChoiceChip(
                          label: const Text('예',
                              style: TextStyle(
                                  fontWeight: FontWeight.w500,
                                  color: Colors.black)),
                          selected: answers[index] == '예',
                          selectedColor: const Color(0xFF3B82F6),
                          onSelected: (_) => _updateAnswer(index, '예'),
                          backgroundColor: Colors.grey[200],
                          labelStyle: TextStyle(
                              color: answers[index] == '예'
                                  ? Colors.white
                                  : Colors.black87),
                        ),
                        ChoiceChip(
                          label: const Text('아니오',
                              style: TextStyle(
                                  fontWeight: FontWeight.w500,
                                  color: Colors.black)),
                          selected: answers[index] == '아니오',
                          selectedColor: Colors.redAccent,
                          onSelected: (_) => _updateAnswer(index, '아니오'),
                          backgroundColor: Colors.grey[200],
                          labelStyle: TextStyle(
                              color: answers[index] == '아니오'
                                  ? Colors.white
                                  : Colors.black87),
                        ),
                      ],
                    ),
                  ],
                ),
              );
            }),

            const SizedBox(height: 10),
            const Divider(thickness: 1, color: Colors.grey, height: 30),
            const SizedBox(height: 10),

            // 제출 버튼
            Container(
              width: double.infinity,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                gradient: LinearGradient(
                  colors: isAllAnswered
                      ? [const Color(0xFF3B82F6), const Color(0xFF60A5FA)]
                      : [Colors.grey, Colors.grey],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: ElevatedButton(
                onPressed: isAllAnswered
                    ? () async {
                  int totalScore = calculateScore();

                  Future<void> sendQuestionScore(int totalScore) async {
                    try {
                      final prefs =
                      await SharedPreferences.getInstance();
                      int? scoreId = prefs.getInt('currentScoreId');
                      var url = Uri.parse(
                          "http://10.0.2.2:8080/api/question/submit?scoreId=$scoreId&score=$totalScore");
                      var response = await http.post(url);
                      if (response.statusCode == 200) {
                        debugPrint("서버 저장 성공");
                      } else {
                        debugPrint("서버 저장 실패: ${response.statusCode}");
                      }
                    } catch (e) {
                      debugPrint("에러 발생: $e");
                    }
                  }

                  Future<void> calculateFinalScore() async {
                    final prefs = await SharedPreferences.getInstance();
                    int? scoreId = prefs.getInt('currentScoreId');
                    var url = Uri.parse(
                        "http://10.0.2.2:8080/api/final/calculate?scoreId=$scoreId");
                    var response = await http.post(url);
                    if (response.statusCode == 200) {
                      debugPrint("최종점수 계산 완료");
                    } else {
                      debugPrint("계산 실패");
                    }
                  }

                  await sendQuestionScore(totalScore);
                  await calculateFinalScore();

                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) =>
                          ResultScreen(cameras: widget.cameras),
                    ),
                  );
                }
                    : null,
                style: ElevatedButton.styleFrom(
                  elevation: 0,
                  shadowColor: Colors.transparent,
                  backgroundColor: Colors.transparent,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text(
                  '제출하기',
                  style: TextStyle(
                      fontSize: 18, color: Colors.white, fontWeight: FontWeight.bold),
                ),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
