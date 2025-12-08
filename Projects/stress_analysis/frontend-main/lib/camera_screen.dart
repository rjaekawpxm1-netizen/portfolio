import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'recording_screen.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:path_provider/path_provider.dart';

class CameraScreen extends StatefulWidget {
  final List<CameraDescription> cameras;

  const CameraScreen({super.key, required this.cameras});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  bool _isRecording = false;
  bool _isConfirmed = false;
  XFile? _recordedVideo;

  @override
  void initState() {
    super.initState();
    _controller = CameraController(
      widget.cameras.first,
      ResolutionPreset.medium,
      enableAudio: true,
    );
    _initializeControllerFuture = _controller.initialize();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> uploadVideo(String path) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      int? scoreId = prefs.getInt('currentScoreId');

      if (scoreId == null) {
        print('❌ [uploadVideo] scoreId가 null입니다. 영상 업로드 중단');
        return;
      }

      var request = http.MultipartRequest(
        'POST',
        Uri.parse('http://10.0.2.2:8080/api/video'),
      );
      request.files.add(await http.MultipartFile.fromPath('file', path));
      request.fields['scoreId'] = scoreId.toString();

      var response = await request.send();

      if (response.statusCode == 200) {
        String respStr = await response.stream.bytesToString();
        print('✅ 영상 점수: $respStr');
      } else {
        print('❌ 영상 업로드 실패 - 상태 코드: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [uploadVideo] 예외 발생: $e');
    }
  }

  Future<void> safeUploadVideo(XFile videoFile) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final safePath = '${directory.path}/video_${DateTime.now().millisecondsSinceEpoch}.mp4';

      await videoFile.saveTo(safePath);
      print('✅ 영상 로컬 저장 완료: $safePath');

      await uploadVideo(safePath);
      print('✅ 영상 업로드 함수 완료');
    } catch (e) {
      print('❌ [safeUploadVideo] 예외 발생: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('카메라 촬영'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      extendBodyBehindAppBar: true,
      body: FutureBuilder<void>(
        future: _initializeControllerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            return Stack(
              children: [
                Positioned.fill(child: CameraPreview(_controller)),
                Positioned(
                  bottom: 40,
                  left: 0,
                  right: 0,
                  child: Center(
                    child: GestureDetector(
                      onTap: () async {
                        try {
                          await _initializeControllerFuture;

                          if (!_isRecording && !_isConfirmed) {
                            await _controller.startVideoRecording();
                            setState(() {
                              _isRecording = true;
                            });
                          } else if (_isRecording && !_isConfirmed) {
                            final file = await _controller.stopVideoRecording();
                            setState(() {
                              _isRecording = false;
                              _isConfirmed = true;
                              _recordedVideo = file;
                            });

                            // 업로드 + 화면 전환
                            await safeUploadVideo(file);

                            if (mounted) {
                              Navigator.pushReplacement(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => RecordingScreen(cameras: widget.cameras),
                                ),
                              );
                            }
                          }
                        } catch (e) {
                          print("❌ 녹화 처리 중 오류 발생: $e");
                        }
                      },
                      child: Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: Colors.white.withOpacity(0.2),
                          border: Border.all(
                            color: Colors.white,
                            width: 4,
                          ),
                        ),
                        child: Center(
                          child: Icon(
                            _isRecording ? Icons.stop : Icons.videocam,
                            size: 36,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            );
          } else {
            return const Center(child: CircularProgressIndicator());
          }
        },
      ),
    );
  }
}
