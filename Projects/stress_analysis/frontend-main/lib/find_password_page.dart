import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'login_page.dart';

class FindPasswordPage extends StatefulWidget {
  const FindPasswordPage({super.key});

  @override
  State<FindPasswordPage> createState() => _FindPasswordPageState();
}

class _FindPasswordPageState extends State<FindPasswordPage> {
  final emailController = TextEditingController();
  final codeController = TextEditingController();
  final newPasswordController = TextEditingController();
  final confirmPasswordController = TextEditingController();

  String _temporaryCode = '';
  bool _isCodeVerified = false;

  void sendVerificationCode() async {
    final email = emailController.text.trim();
    if (email.isEmpty || !email.contains('@')) {
      _showAlert('오류', '유효한 이메일 주소를 입력해주세요.');
      return;
    }

    try {
      final url = Uri.parse('http://10.0.2.2:8080/api/auth/send-verification-code');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );

      if (response.statusCode == 200) {
        try {
          final decoded = jsonDecode(response.body);
          if (decoded is Map<String, dynamic> && decoded.containsKey('code')) {
            setState(() {
              _temporaryCode = decoded['code'];
              _isCodeVerified = false;
            });
            _showAlert('성공', '인증 코드가 발송되었습니다. 이메일을 확인해주세요. (개발용 코드: $_temporaryCode)');
          } else if (decoded is List && decoded.isNotEmpty) {
            final first = decoded.first;
            if (first is Map && first.containsKey('code')) {
              setState(() {
                _temporaryCode = first['code'];
                _isCodeVerified = false;
              });
              _showAlert('성공', '인증 코드가 발송되었습니다. 이메일을 확인해주세요. (개발용 코드: $_temporaryCode)');
            } else {
              setState(() {
                _temporaryCode = '';
                _isCodeVerified = false;
              });
              _showAlert('성공', '인증 코드가 발송되었습니다. 이메일을 확인해주세요.');
            }
          } else {
            setState(() {
              _temporaryCode = '';
              _isCodeVerified = false;
            });
            _showAlert('성공', '인증 코드가 발송되었습니다. 이메일을 확인해주세요.');
          }
        } catch (_) {
          setState(() {
            _temporaryCode = '';
            _isCodeVerified = false;
          });
          _showAlert('성공', '인증 코드가 발송되었습니다. 이메일을 확인해주세요.');
        }
      } else if (response.statusCode == 404) {
        setState(() {
          _temporaryCode = '';
          _isCodeVerified = false;
        });
        _showAlert('오류', '해당 이메일의 사용자를 찾을 수 없습니다.');
      } else {
        setState(() {
          _temporaryCode = '';
          _isCodeVerified = false;
        });
        final errorBody = jsonDecode(response.body);
        _showAlert('오류', '인증 코드 발송 실패: ${errorBody['message'] ?? '알 수 없는 오류'}');
      }
    } catch (e) {
      setState(() {
        _temporaryCode = '';
        _isCodeVerified = false;
      });
      _showAlert('오류', '네트워크 오류 또는 서버 응답 없음: $e');
    }
  }

  void _verifyCode() {
    final enteredCode = codeController.text.trim();
    if (_temporaryCode.isNotEmpty && enteredCode == _temporaryCode) {
      setState(() {
        _isCodeVerified = true;
      });
      _showAlert('성공', '인증이 완료되었습니다. 이제 비밀번호를 재설정할 수 있습니다.');
    } else {
      setState(() {
        _isCodeVerified = false;
      });
      _showAlert('실패', '인증번호가 올바르지 않습니다.');
    }
  }

  void resetPassword() async {
    if (!_isCodeVerified) {
      _showAlert('오류', '먼저 인증을 완료해주세요.');
      return;
    }

    final email = emailController.text.trim();
    final code = codeController.text.trim();
    final newPassword = newPasswordController.text.trim();
    final confirmPassword = confirmPasswordController.text.trim();

    if (email.isEmpty || code.isEmpty || newPassword.isEmpty || confirmPassword.isEmpty) {
      _showAlert('오류', '모든 필드를 입력해주세요.');
      return;
    }

    if (newPassword != confirmPassword) {
      _showAlert('오류', '새 비밀번호와 확인 비밀번호가 일치하지 않습니다.');
      return;
    }

    try {
      final url = Uri.parse('http://10.0.2.2:8080/api/auth/reset-password');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'code': code,
          'newPassword': newPassword,
        }),
      );

      if (response.statusCode == 200) {
        _showAlert('성공', '비밀번호가 성공적으로 재설정되었습니다. 로그인해주세요.');
        Navigator.pushAndRemoveUntil(
          context,
          MaterialPageRoute(builder: (context) => const LoginPage()),
              (Route<dynamic> route) => false,
        );
      } else {
        final decoded = jsonDecode(response.body);
        _showAlert('오류', '비밀번호 재설정 실패: ${decoded['message'] ?? '서버 오류'}');
      }
    } catch (e) {
      _showAlert('오류', '네트워크 오류 또는 서버 응답 없음: $e');
    }
  }

  void _showAlert(String title, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('확인'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    emailController.dispose();
    codeController.dispose();
    newPasswordController.dispose();
    confirmPasswordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: const BackButton(color: Colors.white),
        title: const Text('비밀번호 찾기', style: TextStyle(color: Colors.white)),
        centerTitle: true,
        backgroundColor: const Color(0xFF3B82F6),
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 30),
            TextField(
              controller: emailController,
              decoration: InputDecoration(
                hintText: '이메일 주소 입력',
                suffix: TextButton(
                  onPressed: sendVerificationCode,
                  child: const Text('인증번호 받기'),
                ),
                border: const UnderlineInputBorder(),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: codeController,
                    decoration: const InputDecoration(
                      hintText: '인증번호 4자리 입력',
                      border: UnderlineInputBorder(),
                    ),
                    keyboardType: TextInputType.number,
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _verifyCode,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _isCodeVerified ? Colors.green : const Color(0xFF3B82F6),
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('인증확인'),
                ),
              ],
            ),
            if (_temporaryCode.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 10.0),
                child: Text(
                  '개발용 임시 코드: $_temporaryCode',
                  style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
                ),
              ),
            const SizedBox(height: 24),
            if (_isCodeVerified)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TextField(
                    controller: newPasswordController,
                    decoration: const InputDecoration(
                      hintText: '새 비밀번호 입력',
                      border: UnderlineInputBorder(),
                    ),
                    obscureText: true,
                  ),
                  const SizedBox(height: 24),
                  TextField(
                    controller: confirmPasswordController,
                    decoration: const InputDecoration(
                      hintText: '새 비밀번호 확인',
                      border: UnderlineInputBorder(),
                    ),
                    obscureText: true,
                  ),
                  const SizedBox(height: 40),
                  SizedBox(
                    width: double.infinity,
                    height: 45,
                    child: ElevatedButton(
                      onPressed: resetPassword,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF3B82F6),
                        foregroundColor: Colors.white,
                      ),
                      child: const Text('비밀번호 재설정'),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
