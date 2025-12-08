import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'user_data.dart';
import 'my_page.dart';

class ChangePasswordPage extends StatefulWidget {
  const ChangePasswordPage({super.key});

  @override
  State<ChangePasswordPage> createState() => _ChangePasswordPageState();
}

class _ChangePasswordPageState extends State<ChangePasswordPage> {
  final currentPasswordController = TextEditingController();
  final newPasswordController = TextEditingController();
  final confirmPasswordController = TextEditingController();

  @override
  void dispose() {
    currentPasswordController.dispose();
    newPasswordController.dispose();
    confirmPasswordController.dispose();
    super.dispose();
  }

  void _changePassword() async {
    final current = currentPasswordController.text.trim();
    final newPw = newPasswordController.text.trim();
    final confirm = confirmPasswordController.text.trim();

    if (newPw != confirm) {
      _showSnackBar('❌ 새 비밀번호가 일치하지 않습니다.');
      return;
    }

    if (current.isEmpty || newPw.isEmpty || confirm.isEmpty) {
      _showSnackBar('⚠️ 모든 필드를 입력해주세요.');
      return;
    }

    final userEmail = UserData.email;

    if (userEmail == null || userEmail.isEmpty) {
      _showSnackBar('로그인 정보가 없습니다. 다시 로그인해주세요.');
      return;
    }

    try {
      final url = Uri.parse('http://10.0.2.2:8080/api/auth/change-password');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': userEmail,
          'currentPassword': current,
          'newPassword': newPw,
        }),
      );

      if (response.statusCode == 200) {
        _showSnackBar('✅ 비밀번호가 성공적으로 변경되었습니다.');
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const MyPage()),
        );
      } else {
        final errorBody = jsonDecode(response.body);
        _showSnackBar('비밀번호 변경 실패: ${errorBody['message'] ?? '알 수 없는 오류'}');
      }
    } catch (e) {
      _showSnackBar('비밀번호 변경 중 오류 발생: ${e.toString()}');
    }
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    final themeBlue = const Color(0xFF3B82F6);

    return WillPopScope(
      onWillPop: () async {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const MyPage()),
        );
        return false;
      },
      child: Scaffold(
        backgroundColor: const Color(0xfff9fafb),
        appBar: AppBar(
          backgroundColor: themeBlue,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back, color: Colors.white),
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const MyPage()),
              );
            },
          ),
          centerTitle: true,
          title: const Text(
            '비밀번호 변경',
            style: TextStyle(
              fontSize: 18,
              color: Colors.white,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 36),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '🔐 보안을 위해 비밀번호를 변경하세요.',
                  style: TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 30),

                _buildTextField(
                  controller: currentPasswordController,
                  label: '현재 비밀번호',
                  icon: Icons.lock_outline,
                  obscure: true,
                ),
                const SizedBox(height: 20),

                _buildTextField(
                  controller: newPasswordController,
                  label: '새 비밀번호',
                  icon: Icons.vpn_key_outlined,
                  obscure: true,
                ),
                const SizedBox(height: 20),

                _buildTextField(
                  controller: confirmPasswordController,
                  label: '비밀번호 확인',
                  icon: Icons.check_circle_outline,
                  obscure: true,
                ),

                const SizedBox(height: 40),

                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: themeBlue,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                      elevation: 2,
                    ),
                    onPressed: _changePassword,
                    child: const Text(
                      '비밀번호 변경하기',
                      style: TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
              ],
            ),
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
  }) {
    return TextField(
      controller: controller,
      obscureText: obscure,
      decoration: InputDecoration(
        prefixIcon: Icon(icon, color: Colors.grey[600]),
        labelText: label,
        labelStyle: const TextStyle(
          color: Colors.black87,
          fontSize: 15,
          fontWeight: FontWeight.w500,
        ),
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
