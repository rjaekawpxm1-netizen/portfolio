import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/services.dart';
import 'signup_page.dart'; // PhoneNumberFormatter 포함
import 'user_data.dart';
import 'my_page.dart';

class MyInfoPage extends StatefulWidget {
  const MyInfoPage({super.key});

  @override
  State<MyInfoPage> createState() => _MyInfoPageState();
}

class _MyInfoPageState extends State<MyInfoPage> {
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  String _email = UserData.email ?? '';

  @override
  void initState() {
    super.initState();
    _loadUserInfo();
  }

  Future<void> _loadUserInfo() async {
    if (_email.isEmpty) {
      _showAlert('오류', '로그인된 사용자 정보가 없습니다.');
      return;
    }
    try {
      final url = Uri.parse(
          'http://10.0.2.2:8080/api/auth/user-info?email=${Uri.encodeComponent(_email)}');
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final userInfo = jsonDecode(response.body);
        setState(() {
          _nameController.text = userInfo['name'] ?? '';
          _phoneController.text = userInfo['phone'] ?? '';
        });
      } else if (response.statusCode == 404) {
        _showAlert('오류', '사용자 정보를 찾을 수 없습니다.');
      } else {
        final errorBody = jsonDecode(response.body);
        _showAlert(
            '오류',
            '사용자 정보 로드 실패: 오류 코드 ${response.statusCode}\n'
                '${errorBody['message'] ?? '알 수 없는 오류'}');
      }
    } catch (e) {
      _showAlert('오류', '사용자 정보 로드 중 오류 발생: ${e.toString()}');
    }
  }

  void _updateUserInfo() async {
    final updatedName = _nameController.text.trim();
    final updatedPhone = _phoneController.text.trim().replaceAll('-', '');

    if (_email.isEmpty || updatedName.isEmpty || updatedPhone.isEmpty) {
      _showAlert('오류', '모든 필드를 입력해주세요.');
      return;
    }

    final phoneRegex = RegExp(r'^[0-9]+$');
    if (!phoneRegex.hasMatch(updatedPhone) ||
        (updatedPhone.length != 10 && updatedPhone.length != 11)) {
      _showAlert('오류', '올바른 전화번호 형식을 입력해주세요 (숫자 10~11자리).');
      return;
    }

    try {
      final url = Uri.parse('http://10.0.2.2:8080/api/auth/user-info');
      final response = await http.put(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': _email,
          'name': updatedName,
          'phone': updatedPhone,
        }),
      );

      if (response.statusCode == 200) {
        _showAlert('성공', '사용자 정보가 성공적으로 업데이트되었습니다.');
      } else if (response.statusCode == 404) {
        _showAlert('오류', '사용자를 찾을 수 없어 정보를 업데이트할 수 없습니다.');
      } else {
        final errorBody = jsonDecode(response.body);
        _showAlert(
            '오류',
            '사용자 정보 업데이트 실패: 오류 코드 ${response.statusCode}\n'
                '${errorBody['message'] ?? '알 수 없는 오류'}');
      }
    } catch (e) {
      _showAlert('오류', '사용자 정보 업데이트 중 오류 발생: ${e.toString()}');
    }
  }

  void _showAlert(String title, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('확인', style: TextStyle(color: Color(0xFF3B82F6))),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final themeBlue = const Color(0xFF3B82F6);

    return Scaffold(
      backgroundColor: const Color(0xfff9fafb),
      appBar: AppBar(
        backgroundColor: themeBlue,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.white),
          onPressed: () {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (context) => const MyPage()),
            );
          },
        ),
        title: const Text(
          '내 정보',
          style: TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 36),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Icon(Icons.manage_accounts_rounded,
                  color: Color(0xFF3B82F6), size: 80),
              const SizedBox(height: 20),
              const Text(
                '회원님의 정보를 확인하고 수정하세요',
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w600,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 40),

              // 이메일은 표시만
              Container(
                width: double.infinity,
                padding:
                const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFE5E7EB)),
                ),
                child: Text(
                  '이메일: $_email',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                    color: Colors.black87,
                  ),
                ),
              ),
              const SizedBox(height: 25),

              _buildTextField(_nameController, '이름', Icons.person_outline),
              const SizedBox(height: 20),
              _buildTextField(_phoneController, '전화번호', Icons.phone_android_outlined,
                  hint: '예: 010-1234-5678',
                  keyboardType: TextInputType.phone,
                  inputFormatters: [
                    FilteringTextInputFormatter.digitsOnly,
                    PhoneNumberFormatter(),
                  ]),
              const SizedBox(height: 40),

              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _updateUserInfo,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: themeBlue,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10)),
                    elevation: 3,
                  ),
                  child: const Text(
                    '정보 수정',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 17,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(
      TextEditingController controller,
      String label,
      IconData icon, {
        String? hint,
        TextInputType keyboardType = TextInputType.text,
        List<TextInputFormatter>? inputFormatters,
      }) {
    return TextField(
      controller: controller,
      keyboardType: keyboardType,
      inputFormatters: inputFormatters,
      decoration: InputDecoration(
        prefixIcon: Icon(icon, color: Colors.grey[600]),
        labelText: label,
        hintText: hint,
        filled: true,
        fillColor: Colors.white,
        labelStyle: const TextStyle(
          color: Colors.black87,
          fontSize: 15,
          fontWeight: FontWeight.w500,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFFe5e7eb)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF3B82F6), width: 1.5),
        ),
      ),
    );
  }
}
