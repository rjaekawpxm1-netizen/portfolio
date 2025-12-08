import 'dart:async';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';

class MeditationPage extends StatefulWidget {
  const MeditationPage({super.key});

  @override
  State<MeditationPage> createState() => _MeditationPageState();
}

class _MeditationPageState extends State<MeditationPage> {
  final AudioPlayer _audioPlayer = AudioPlayer();
  Timer? _timer;
  int _remainingSeconds = 300; // 5분
  bool _isMeditating = false;

  String get _formattedTime {
    final minutes = (_remainingSeconds ~/ 60).toString().padLeft(2, '0');
    final seconds = (_remainingSeconds % 60).toString().padLeft(2, '0');
    return "$minutes:$seconds";
  }

  Future<void> _startMeditation() async {
    if (_isMeditating) return;

    setState(() => _isMeditating = true);

    // 명상 음악 재생
    await _audioPlayer.play(AssetSource('meditation_music.mp3'));

    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_remainingSeconds > 0) {
        setState(() => _remainingSeconds--);
      } else {
        _stopMeditation();
      }
    });
  }

  Future<void> _stopMeditation() async {
    _timer?.cancel();
    await _audioPlayer.stop();
    setState(() {
      _isMeditating = false;
      _remainingSeconds = 300;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('명상 세션이 종료되었습니다 🌱')),
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    _audioPlayer.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
        title: const Text(
          '명상하기',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
      ),
      body: Stack(
        fit: StackFit.expand,
        children: [
          // ✅ 배경 이미지
          Image.asset(
            'assets/meditation_bg.png',
            fit: BoxFit.cover,
          ),

          // ✅ 블러 + 색 오버레이
          BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 6, sigmaY: 6),
            child: Container(
              color: Colors.black.withOpacity(0.35),
            ),
          ),

          // ✅ 명상 내용
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                '마음을 비우고 호흡에 집중하세요 🍃',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 17,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 30),
              Text(
                _formattedTime,
                style: const TextStyle(
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  letterSpacing: 2,
                ),
              ),
              const SizedBox(height: 40),
              ElevatedButton.icon(
                onPressed: _isMeditating ? _stopMeditation : _startMeditation,
                icon: Icon(
                  _isMeditating ? Icons.stop : Icons.play_arrow,
                  color: Colors.white,
                ),
                label: Text(
                  _isMeditating ? '명상 중지하기' : '명상 시작하기',
                  style: const TextStyle(color: Colors.white, fontSize: 16),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor:
                  _isMeditating ? Colors.redAccent : Colors.green.shade400,
                  padding:
                  const EdgeInsets.symmetric(horizontal: 30, vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(25),
                  ),
                  elevation: 5,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
