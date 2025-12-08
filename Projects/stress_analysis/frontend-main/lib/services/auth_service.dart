import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  static const String baseUrl = 'http://10.0.2.2:8080';

  Future<bool> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      print("🟦 로그인 요청 완료: ${response.statusCode}");
      print("📄 응답 본문: ${response.body}");

      if (response.statusCode == 200) {
        // 백엔드가 단순 텍스트("로그인 성공")를 반환해도 통과
        return true;
      } else {
        print("❌ 로그인 실패: ${response.body}");
        return false;
      }
    } catch (e) {
      print("🚨 로그인 중 오류 발생: $e");
      return false;
    }
  }

  Future<bool> signup(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/signup'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      print("🟩 회원가입 응답 코드: ${response.statusCode}");
      print("📄 응답 본문: ${response.body}");

      if (response.statusCode == 200 || response.statusCode == 201) {
        return true;
      } else {
        print("❌ 회원가입 실패: ${response.body}");
        return false;
      }
    } catch (e) {
      print("🚨 회원가입 중 오류 발생: $e");
      return false;
    }
  }
}
