import 'package:flutter/material.dart';
import 'package:kakao_flutter_sdk_user/kakao_flutter_sdk_user.dart';

import 'login_page.dart';
import 'signup_page.dart';

class WelcomePage extends StatelessWidget {
  const WelcomePage({super.key});

  void _goToLogin(BuildContext context) {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const LoginPage()),
    );
  }

  void _goToSignup(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const SignupPage()),
    );
  }

  Future<void> _kakaoLogin(BuildContext context) async {
    try {
      bool isInstalled = await isKakaoTalkInstalled();

      OAuthToken token = isInstalled
          ? await UserApi.instance.loginWithKakaoTalk()
          : await UserApi.instance.loginWithKakaoAccount();

      print('카카오 로그인 성공: ${token.accessToken}');

      User user = await UserApi.instance.me();
      print('사용자 닉네임: ${user.kakaoAccount?.profile?.nickname}');
      print('사용자 이메일: ${user.kakaoAccount?.email}');

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content:
          Text('${user.kakaoAccount?.profile?.nickname}님 환영합니다!'),
          behavior: SnackBarBehavior.floating,
        ),
      );
    } catch (error) {
      print('카카오 로그인 실패: $error');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('카카오 로그인에 실패했습니다.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 28),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // 🔹 앱 로고
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black12,
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  padding: const EdgeInsets.all(24),
                  child: Image.asset(
                    'assets/logo.png',
                    width: 120,
                    height: 120,
                  ),
                ),
                const SizedBox(height: 25),

                // 🔹 앱 소개 문구
                const Text(
                  'AI 감정 기반 분석 서비스',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.black54,
                    letterSpacing: 0.3,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  '당신의 감정, AI가 이해합니다.',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1E3A8A),
                  ),
                ),

                const SizedBox(height: 40),

                // ✅ 카카오 로그인 버튼
                ElevatedButton.icon(
                  onPressed: () => _kakaoLogin(context),
                  icon: const Icon(Icons.chat_bubble_outline,
                      color: Colors.black87),
                  label: const Text(
                    '카카오 계정으로 시작하기',
                    style: TextStyle(
                        color: Colors.black87,
                        fontSize: 16,
                        fontWeight: FontWeight.w500),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFFEE500),
                    foregroundColor: Colors.black87,
                    minimumSize: const Size.fromHeight(50),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 3,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),

                const SizedBox(height: 18),

                // ✅ 이메일 로그인 버튼
                ElevatedButton.icon(
                  onPressed: () => _goToLogin(context),
                  icon: const Icon(Icons.mail_outline, color: Colors.white),
                  label: const Text(
                    '이메일 로그인 (ID/비밀번호 찾기)',
                    style: TextStyle(
                        fontSize: 16,
                        color: Colors.white,
                        fontWeight: FontWeight.w500),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF3B82F6),
                    minimumSize: const Size.fromHeight(50),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    shadowColor: Colors.blueAccent.withOpacity(0.3),
                    elevation: 4,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),

                const SizedBox(height: 12),

                // ✅ 회원가입 버튼
                OutlinedButton.icon(
                  onPressed: () => _goToSignup(context),
                  icon: const Icon(Icons.person_add_alt_1_outlined,
                      color: Color(0xFF3B82F6)),
                  label: const Text(
                    '이메일로 새 계정 만들기',
                    style: TextStyle(
                        fontSize: 16,
                        color: Color(0xFF3B82F6),
                        fontWeight: FontWeight.w600),
                  ),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(
                        color: Color(0xFF3B82F6), width: 1.4),
                    minimumSize: const Size.fromHeight(50),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),

                const SizedBox(height: 30),

                // ✅ 안내 문구
                const Text(
                  '로그인 또는 회원가입을 통해 서비스를 시작하세요',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.black45,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
