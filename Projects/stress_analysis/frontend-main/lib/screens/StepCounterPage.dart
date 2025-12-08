import 'package:flutter/material.dart';
import 'package:pedometer/pedometer.dart';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

class StepCounterPage extends StatefulWidget {
  const StepCounterPage({super.key});

  @override
  State<StepCounterPage> createState() => _StepCounterPageState();
}

class _StepCounterPageState extends State<StepCounterPage> {
  late StreamSubscription<StepCount> _stepCountSubscription;
  int _todaySteps = 0;

  @override
  void initState() {
    super.initState();
    _initPedometer();
  }

  Future<void> _initPedometer() async {
    _stepCountSubscription = Pedometer.stepCountStream.listen(
          (StepCount event) {
        setState(() {
          _todaySteps = event.steps;
        });
      },
      onError: (error) => print('걸음 센서 오류: $error'),
      cancelOnError: true,
    );
  }

  Future<void> _saveSteps() async {
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
        const SnackBar(content: Text('걸음 수가 저장되었습니다!')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('저장 실패 (${response.statusCode})')),
      );
    }
  }

  @override
  void dispose() {
    _stepCountSubscription.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('만보기', style: TextStyle(color: Colors.white)),
        backgroundColor: const Color(0xFF3B82F6),
        centerTitle: true,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                '오늘의 걸음 수',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 20),
              Text(
                '$_todaySteps 걸음',
                style: const TextStyle(
                  fontSize: 40,
                  fontWeight: FontWeight.bold,
                  color: Colors.blueAccent,
                ),
              ),
              const SizedBox(height: 30),
              ElevatedButton.icon(
                onPressed: _saveSteps,
                icon: const Icon(Icons.save, color: Colors.white),
                label: const Text('서버에 저장', style: TextStyle(color: Colors.white)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF3B82F6),
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
