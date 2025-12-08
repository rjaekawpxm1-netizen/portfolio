import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class FindEmailPage extends StatefulWidget {
  const FindEmailPage({super.key});

  @override
  State<FindEmailPage> createState() => _FindEmailPageState();
}

class PhoneNumberFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    final text = newValue.text.replaceAll('-', '');
    if (text.isEmpty) return newValue.copyWith(text: '');
    final buffer = StringBuffer();
    for (int i = 0; i < text.length; i++) {
      buffer.write(text[i]);
      if (i == 2 || i == 6) {
        if (i != text.length - 1) buffer.write('-');
      }
    }
    final formattedText = buffer.toString();
    return newValue.copyWith(
      text: formattedText,
      selection: TextSelection.collapsed(offset: formattedText.length),
    );
  }
}

class _FindEmailPageState extends State<FindEmailPage> {
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _codeController = TextEditingController();

  String _sentCode = '';
  int _timerSeconds = 0;
  Timer? _timer;
  bool _isVerified = false;
  List<String> _foundEmails = [];

  void _sendVerificationCode() {
    final random = Random();
    setState(() {
      _sentCode = (1000 + random.nextInt(9000)).toString();
      _timerSeconds = 60;
      _isVerified = false;
    });
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_timerSeconds == 0) {
        timer.cancel();
      } else {
        setState(() {
          _timerSeconds--;
        });
      }
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('인증번호: $_sentCode')),
    );
  }

  void _verifyCode() {
    if (_codeController.text == _sentCode) {
      setState(() {
        _isVerified = true;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('인증 성공!')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('인증 실패. 다시 시도해주세요.')),
      );
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    _nameController.dispose();
    _phoneController.dispose();
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _findEmails() async {
    final name = _nameController.text.trim();
    final phone = _phoneController.text.trim();
    final phoneWithoutHyphen = phone.replaceAll('-', '');

    if (name.isEmpty || phone.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('이름과 전화번호를 모두 입력해주세요.')),
      );
      return;
    }

    final phoneDigitsOnly = phone.replaceAll('-', '');
    final phoneRegex = RegExp(r'^[0-9]+$');
    if (!phoneRegex.hasMatch(phoneDigitsOnly) ||
        (phoneDigitsOnly.length != 10 && phoneDigitsOnly.length != 11)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('올바른 전화번호 형식을 입력해주세요 (숫자 10-11자리).')),
      );
      return;
    }

    try {
      final url = Uri.parse(
          'http://10.0.2.2:8080/api/auth/find-emails?name=${Uri.encodeComponent(name)}&phone=${Uri.encodeComponent(phoneWithoutHyphen)}');
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        List<String> emails = [];

        if (decoded is Map<String, dynamic>) {
          if (decoded.containsKey('email')) {
            emails.add(decoded['email']);
          } else if (decoded.containsKey('emails')) {
            emails = List<String>.from(decoded['emails']);
          }
        } else if (decoded is List) {
          emails = List<String>.from(decoded);
        }

        setState(() {
          _foundEmails = emails;
        });

        if (emails.isNotEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('${emails.length}개의 이메일을 찾았습니다.')),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('해당 정보와 일치하는 사용자를 찾을 수 없습니다.')),
          );
        }
      } else if (response.statusCode == 404) {
        setState(() {
          _foundEmails = [];
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('해당 정보와 일치하는 사용자를 찾을 수 없습니다.')),
        );
      } else {
        setState(() {
          _foundEmails = [];
        });
        final errorBody = jsonDecode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content: Text(
                  '이메일 찾기 실패: 오류 코드 ${response.statusCode}\n${errorBody['message'] ?? '알 수 없는 오류'}')),
        );
      }
    } catch (e) {
      setState(() {
        _foundEmails = [];
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('이메일 찾기 중 오류 발생: ${e.toString()}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: const BackButton(color: Colors.white),
        title: const Text('이메일 찾기', style: TextStyle(color: Colors.white)),
        centerTitle: true,
        backgroundColor: const Color(0xFF3B82F6),
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 60),
            TextField(
              controller: _nameController,
              decoration: InputDecoration(
                labelText: '이름',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                filled: true,
                fillColor: Colors.grey[200],
              ),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _phoneController,
              decoration: InputDecoration(
                labelText: '전화번호',
                hintText: '예: 010-1234-5678',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                filled: true,
                fillColor: Colors.grey[200],
              ),
              keyboardType: TextInputType.phone,
              inputFormatters: [
                FilteringTextInputFormatter.digitsOnly,
                PhoneNumberFormatter(),
              ],
            ),
            const SizedBox(height: 30),
            ElevatedButton(
              onPressed: _findEmails,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF3B82F6),
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 48),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: const Text('이메일 찾기'),
            ),
            const SizedBox(height: 30),
            if (_foundEmails.isNotEmpty)
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '찾은 이메일 목록:',
                      style:
                      TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Expanded(
                      child: ListView.builder(
                        itemCount: _foundEmails.length,
                        itemBuilder: (context, index) {
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 4.0),
                            child: Text(
                              _foundEmails[index],
                              style: const TextStyle(
                                  fontSize: 18, color: Colors.blue),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
