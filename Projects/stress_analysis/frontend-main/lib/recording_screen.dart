import 'dart:io';
import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:http/http.dart' as http;
import 'question_screen.dart';
import 'package:camera/camera.dart';
import 'package:shared_preferences/shared_preferences.dart';

class RecordingScreen extends StatefulWidget {
  final List<CameraDescription> cameras;

  const RecordingScreen({super.key, required this.cameras});

  @override
  State<RecordingScreen> createState() => _RecordingScreenState();
}

class _RecordingScreenState extends State<RecordingScreen> {
  bool _isRecording = false;
  late final Record recorder;

  @override
  void initState() {
    super.initState();
    recorder = Record();
  }

  Future<String> _getFilePath() async {
    final directory = await getApplicationDocumentsDirectory();
    return '${directory.path}/audio.wav';
  }

  void _toggleRecording() async {
    setState(() {
      _isRecording = !_isRecording;
    });

    if (_isRecording) {
      final path = await _getFilePath();
      await recorder.start(path: path, encoder: AudioEncoder.wav,);
    } else {
      await recorder.stop();
      final path = await _getFilePath();
      await uploadAudio(path);

      if (mounted) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => QuestionScreen(cameras: widget.cameras),
          ),
        );
      }
    }
  }

  Future<void> uploadAudio(String path) async {
    var request = http.MultipartRequest('POST', Uri.parse('http://10.0.2.2:8080/api/audio'));
    request.files.add(await http.MultipartFile.fromPath('file', path));

    final prefs = await SharedPreferences.getInstance();
    int? scoreId = prefs.getInt('currentScoreId');

     if (scoreId == null) {
    print('❌ scoreId가 null입니다. 업로드 중단');
    return;
  }
    request.fields['scoreId'] = scoreId.toString();

    var response = await request.send();

    if (response.statusCode == 200) {
      String respStr = await response.stream.bytesToString();
      print('음성 점수: $respStr');
    } else {
      print('음성 업로드 실패');
    }
  }

  @override
  void dispose() {
    recorder.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xfff8f9fa),
      appBar: AppBar(
        backgroundColor: const Color(0xFF3B82F6),
        elevation: 1,
        title: const Text('음성 녹음', style: TextStyle(color: Colors.white)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        centerTitle: true,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 30),
          child: Column(
            mainAxisSize: MainAxisSize.max,
            mainAxisAlignment: MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Text(
                '아래의 문장을\n또박또박 읽어주세요.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.w500),
              ),
              const SizedBox(height: 40),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 30),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.blueAccent, width: 1.2),
                ),
                child: const Text(
                  '“네가 어떤 모습이든 그대로도 충분히 아름다워.”',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
              ),
              const Spacer(),
              GestureDetector(
                onTap: _toggleRecording,
                child: Column(
                  children: [
                    AnimatedContainer(
                      duration: const Duration(milliseconds: 300),
                      height: 100,
                      width: 100,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: _isRecording ? Colors.red : Colors.blue,
                        boxShadow: [
                          BoxShadow(
                            color: (_isRecording ? Colors.redAccent : Colors.blueAccent).withOpacity(0.4),
                            blurRadius: 20,
                            spreadRadius: 5,
                          ),
                        ],
                      ),
                      child: Icon(
                        _isRecording ? Icons.stop : Icons.mic,
                        color: Colors.white,
                        size: 50,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      _isRecording ? '녹음 중...' : '눌러서 녹음 시작',
                      style: const TextStyle(fontSize: 16, color: Colors.black54),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 50),
            ],
          ),
        ),
      ),
    );
  }
}
