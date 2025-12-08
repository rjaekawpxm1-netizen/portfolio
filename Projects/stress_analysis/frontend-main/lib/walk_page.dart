import 'package:flutter/material.dart';
import 'package:pedometer/pedometer.dart';
import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class WalkPage extends StatefulWidget {
  const WalkPage({super.key});

  @override
  State<WalkPage> createState() => _WalkPageState();
}

class _WalkPageState extends State<WalkPage> {
  late StreamSubscription<StepCount> _stepSubscription;
  int _todaySteps = 0;

  @override
  void initState() {
    super.initState();
    _initPedometer();
  }

  @override
  void dispose() {
    _stepSubscription.cancel();
    super.dispose();
  }

  Future<void> _initPedometer() async {
    try {
      _stepSubscription = Pedometer.stepCountStream.listen(
            (StepCount event) {
          if (mounted) {
            setState(() {
              _todaySteps = event.steps;
            });
          }
        },
        onError: (error) => print('걸음 센서 오류: $error'),
        cancelOnError: true,
      );
    } catch (e) {
      print("만보기 초기화 오류: $e");
    }
  }

  Future<void> _saveStepsToServer() async {
    final prefs = await SharedPreferences.getInstance();
    final email = prefs.getString('loggedInUserEmail') ?? '';

    if (email.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('로그인 정보가 없습니다.')),
      );
      return;
    }

    final url = Uri.parse('http://10.0.2.2:8080/api/steps/save');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'steps': _todaySteps,
      }),
    );

    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('걸음 수가 서버에 저장되었습니다!')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('저장 실패 (${response.statusCode})')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF9FAFB),
      appBar: AppBar(
        title: const Text(
          '산책하기',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.green[600],
        centerTitle: true,
        elevation: 0,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 30.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.directions_walk, size: 80, color: Colors.green),
              const SizedBox(height: 20),
              const Text(
                '걸음을 걸으며 몸과 마음을 리프레시하세요!',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.black87,
                  fontSize: 17,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 40),

              // 🔹 걸음 수 표시
              Container(
                padding: const EdgeInsets.all(35),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.green.withOpacity(0.2),
                      blurRadius: 12,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    const Text(
                      '오늘의 걸음 수',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.black54,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '$_todaySteps',
                      style: const TextStyle(
                        fontSize: 42,
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 40),

              // 🔹 서버 저장 버튼
              ElevatedButton.icon(
                onPressed: _saveStepsToServer,
                icon: const Icon(Icons.cloud_upload, color: Colors.white),
                label: const Text(
                  '서버에 걸음 수 저장',
                  style: TextStyle(color: Colors.white, fontSize: 16),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green[600],
                  padding: const EdgeInsets.symmetric(
                      horizontal: 28, vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
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
