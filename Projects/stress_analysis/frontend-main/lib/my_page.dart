import 'package:flutter/material.dart';
import 'my_record.dart';
import 'favorite_record.dart';
import 'my_info_page.dart';
import 'change_password_page.dart';
import 'logout_page.dart';
import 'home_page.dart';
import 'relax_page.dart';

class MyPage extends StatelessWidget {
  const MyPage({super.key});

  void _onBottomTap(BuildContext context, int index) {
    if (index == 0) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const HomePage(cameras: [])),
      );
    } else if (index == 1) {
      // stay on MyPage
    } else if (index == 2) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const RelaxPage()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final List<Map<String, dynamic>> menuItems = [
      {"icon": Icons.person_outline, "title": "내 정보", "page": const MyInfoPage()},
      {"icon": Icons.history, "title": "내 기록", "page": MyRecordPage()},
      {"icon": Icons.star_border, "title": "즐겨찾기 기록", "page": const FavoriteRecordPage()},
      {"icon": Icons.lock_outline, "title": "비밀번호 변경", "page": const ChangePasswordPage()},
      {"icon": Icons.logout, "title": "로그아웃", "page": const LogoutPage()},
    ];

    return Scaffold(
      backgroundColor: const Color(0xFFF9FAFB),
      appBar: AppBar(
        title: const Text(
          '마이페이지',
          style: TextStyle(fontSize: 20, color: Colors.white, fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF3B82F6),
        elevation: 0,
        centerTitle: true,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 20.0),
          child: ListView.builder(
            itemCount: menuItems.length,
            itemBuilder: (context, index) {
              final item = menuItems[index];
              return GestureDetector(
                onTap: () {
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (_) => item["page"]),
                  );
                },
                child: Card(
                  margin: const EdgeInsets.symmetric(vertical: 10),
                  elevation: 3,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  shadowColor: Colors.grey.withOpacity(0.15),
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 20),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(16),
                      gradient: LinearGradient(
                        colors: [Colors.white, Colors.grey.shade50],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(10),
                              decoration: BoxDecoration(
                                color: const Color(0xFF3B82F6).withOpacity(0.1),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Icon(item["icon"], color: const Color(0xFF3B82F6), size: 26),
                            ),
                            const SizedBox(width: 16),
                            Text(
                              item["title"],
                              style: const TextStyle(
                                fontSize: 17,
                                fontWeight: FontWeight.w600,
                                color: Colors.black87,
                              ),
                            ),
                          ],
                        ),
                        const Icon(Icons.chevron_right, color: Colors.grey),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: Colors.white,
        selectedItemColor: const Color(0xFF3B82F6),
        unselectedItemColor: Colors.grey,
        currentIndex: 1, // MyPage
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: '홈'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: '마이페이지'),
          BottomNavigationBarItem(icon: Icon(Icons.spa_outlined), label: '스트레스 해소'),
        ],
        onTap: (index) => _onBottomTap(context, index),
      ),
    );
  }
}
