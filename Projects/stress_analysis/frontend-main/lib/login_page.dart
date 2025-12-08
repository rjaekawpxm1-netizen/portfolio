import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'home_page.dart';
import 'find_email_page.dart';
import 'find_password_page.dart';
import 'welcome_page.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'user_data.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  bool _isLoading = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  Future<void> login() async {
    final email = emailController.text.trim();
    final password = passwordController.text.trim();

    if (email.isEmpty || password.isEmpty) {
      _showAlertDialog('로그인 실패', '이메일과 비밀번호를 모두 입력해주세요.');
      return;
    }

    setState(() => _isLoading = true);

    try {
      final url = Uri.parse('http://10.0.2.2:8080/api/auth/login');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );

      if (response.statusCode == 200) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('userEmail', email);
        await prefs.setString('loggedInUserEmail', email);
        UserData.email = email;

        final cameras = await availableCameras();
        final firstCamera = cameras.first;

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('로그인 성공!')),
          );
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) => HomePage(cameras: [firstCamera]),
            ),
          );
        }
      } else if (response.statusCode == 401) {
        _showAlertDialog('로그인 실패', '이메일 또는 비밀번호가 일치하지 않습니다.');
      } else {
        final errorBody = _parseErrorBody(response.body);
        _showAlertDialog('로그인 실패', errorBody ?? '서버 오류가 발생했습니다.');
      }
    } catch (e) {
      _showAlertDialog('로그인 오류', '네트워크 연결 오류 또는 서버 응답 없음: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  String? _parseErrorBody(String responseBody) {
    try {
      final decoded = jsonDecode(responseBody);
      return decoded['message'];
    } catch (_) {
      return null;
    }
  }

  void _showAlertDialog(String title, String content) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        content: Text(content),
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
  Widget build(BuildContext context) {
    final themeBlue = const Color(0xFF3B82F6);

    return Scaffold(
      backgroundColor: const Color(0xfff9fafb),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: themeBlue,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.white),
          onPressed: () {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (context) => const WelcomePage()),
            );
          },
        ),
        centerTitle: true,
        title: const Text(
          '이메일 로그인',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: Colors.white),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 40),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Icon(Icons.mail_lock_rounded, color: Color(0xFF3B82F6), size: 80),
              const SizedBox(height: 16),
              const Text(
                '계정 정보를 입력해주세요',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: Colors.black87),
              ),
              const SizedBox(height: 36),

              // 🔹 이메일 입력
              _buildTextField(
                controller: emailController,
                label: '이메일 주소',
                icon: Icons.email_outlined,
              ),
              const SizedBox(height: 20),

              // 🔹 비밀번호 입력
              _buildTextField(
                controller: passwordController,
                label: '비밀번호',
                icon: Icons.lock_outline,
                obscure: _obscurePassword,
                suffix: IconButton(
                  icon: Icon(
                    _obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                    color: Colors.grey,
                  ),
                  onPressed: () {
                    setState(() => _obscurePassword = !_obscurePassword);
                  },
                ),
              ),
              const SizedBox(height: 40),

              // 🔹 로그인 버튼
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : login,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: themeBlue,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    elevation: 3,
                  ),
                  child: _isLoading
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text(
                    '로그인',
                    style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                ),
              ),
              const SizedBox(height: 25),

              // 🔹 이메일/비밀번호 찾기
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  TextButton(
                    onPressed: () {
                      Navigator.push(context, MaterialPageRoute(builder: (_) => const FindEmailPage()));
                    },
                    child: const Text('이메일 찾기', style: TextStyle(fontSize: 14, color: Color(0xFF1E40AF))),
                  ),
                  const Text('|', style: TextStyle(fontSize: 14, color: Colors.grey)),
                  TextButton(
                    onPressed: () {
                      Navigator.push(context, MaterialPageRoute(builder: (_) => const FindPasswordPage()));
                    },
                    child: const Text('비밀번호 찾기', style: TextStyle(fontSize: 14, color: Color(0xFF1E40AF))),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool obscure = false,
    Widget? suffix,
  }) {
    return TextField(
      controller: controller,
      obscureText: obscure,
      decoration: InputDecoration(
        prefixIcon: Icon(icon, color: Colors.grey[600]),
        suffixIcon: suffix,
        labelText: label,
        labelStyle: const TextStyle(color: Colors.black87, fontSize: 15, fontWeight: FontWeight.w500),
        filled: true,
        fillColor: Colors.white,
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
