import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'login_page.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class PhoneNumberFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(TextEditingValue oldValue, TextEditingValue newValue) {
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

class SignupPage extends StatefulWidget {
  const SignupPage({super.key});

  @override
  State<SignupPage> createState() => _SignupPageState();
}

class _SignupPageState extends State<SignupPage> {
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  Future<void> _signup() async {
    FocusScope.of(context).unfocus();

    final name = _nameController.text.trim();
    final phone = _phoneController.text.trim();
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();

    final emailRegex = RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');
    if (!emailRegex.hasMatch(email)) {
      _showDialog('회원가입 실패', '유효한 이메일 주소를 입력해주세요.', false);
      return;
    }

    final phoneDigitsOnly = phone.replaceAll('-', '');
    final phoneRegex = RegExp(r'^[0-9]+$');
    if (!phoneRegex.hasMatch(phoneDigitsOnly) ||
        (phoneDigitsOnly.length != 10 && phoneDigitsOnly.length != 11)) {
      _showDialog('회원가입 실패', '올바른 전화번호 형식을 입력해주세요 (숫자 10~11자리).', false);
      return;
    }

    if (name.isEmpty || phone.isEmpty || email.isEmpty || password.isEmpty) {
      _showDialog('회원가입 실패', '모든 필드를 입력해주세요.', false);
      return;
    }

    setState(() => _isLoading = true);

    try {
      final url = Uri.parse('http://10.0.2.2:8080/api/auth/signup');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'name': name,
          'phone': phoneDigitsOnly,
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        _showDialog('회원가입 성공', '회원가입이 완료되었습니다.\n로그인 페이지로 이동합니다.', true);
      } else {
        final msg = _extractMessage(response.body);
        _showDialog('회원가입 실패', msg, false);
      }
    } catch (e) {
      _showDialog('회원가입 오류', '네트워크 오류 또는 서버 응답 없음: $e', false);
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showDialog(String title, String message, bool success) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              if (success) {
                Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => const LoginPage()));
              }
            },
            child: Text('확인', style: TextStyle(color: success ? const Color(0xFF3B82F6) : Colors.redAccent)),
          ),
        ],
      ),
    );
  }

  String _extractMessage(String body) {
    try {
      final decoded = jsonDecode(body);
      return decoded['message'] ?? '알 수 없는 오류가 발생했습니다.';
    } catch (_) {
      return body;
    }
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
        title: const Text(
          '회원가입',
          style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w600),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 36),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const Icon(Icons.person_add_alt_1_rounded, color: Color(0xFF3B82F6), size: 80),
            const SizedBox(height: 16),
            const Text(
              'AI 감정 분석 서비스에 오신 것을 환영합니다',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.w600, color: Colors.black87),
            ),
            const SizedBox(height: 36),

            _buildTextField(_nameController, '이름', Icons.person_outline),
            const SizedBox(height: 20),
            _buildTextField(_phoneController, '전화번호', Icons.phone_android_outlined,
                hint: '010-1234-5678',
                keyboardType: TextInputType.phone,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly, PhoneNumberFormatter()]),
            const SizedBox(height: 20),
            _buildTextField(_emailController, '이메일 주소', Icons.email_outlined,
                keyboardType: TextInputType.emailAddress),
            const SizedBox(height: 20),
            _buildTextField(_passwordController, '비밀번호', Icons.lock_outline, obscureText: true),

            const SizedBox(height: 40),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _signup,
                style: ElevatedButton.styleFrom(
                  backgroundColor: themeBlue,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  elevation: 3,
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text(
                  '회원가입 완료',
                  style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: Colors.white),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTextField(
      TextEditingController controller,
      String label,
      IconData icon, {
        String? hint,
        bool obscureText = false,
        TextInputType keyboardType = TextInputType.text,
        List<TextInputFormatter>? inputFormatters,
      }) {
    return TextField(
      controller: controller,
      obscureText: obscureText,
      keyboardType: keyboardType,
      inputFormatters: inputFormatters,
      decoration: InputDecoration(
        prefixIcon: Icon(icon, color: Colors.grey[600]),
        labelText: label,
        hintText: hint,
        filled: true,
        fillColor: Colors.white,
        labelStyle: const TextStyle(color: Colors.black87, fontSize: 15, fontWeight: FontWeight.w500),
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

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
}
