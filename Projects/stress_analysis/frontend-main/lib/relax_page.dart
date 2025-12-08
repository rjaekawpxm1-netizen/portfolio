import 'package:flutter/material.dart';
import 'walk_page.dart';
import 'home_page.dart';
import 'my_page.dart';
import 'MeditationPage.dart';

class RelaxPage extends StatelessWidget {
  const RelaxPage({super.key});

  void _onBottomTap(BuildContext context, int index) {
    if (index == 0) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const HomePage(cameras: [])),
      );
    } else if (index == 1) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const MyPage()),
      );
    } else if (index == 2) {
      // 현재 페이지 유지
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F6FB),
      appBar: AppBar(
        title: const Text(
          '스트레스 해소',
          style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
        ),
        backgroundColor: const Color(0xFF3B82F6),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: ListView(
          children: [
            const SizedBox(height: 10),
            const Text(
              '오늘의 스트레스 해소 추천 🌿',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 25),

            // 🔹 산책하기 카드
            GestureDetector(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const WalkPage()),
                );
              },
              child: _activityCard(
                color: Colors.green[50]!,
                icon: Icons.park,
                title: '산책하기',
                subtitle: '걸으면서 스트레스를 해소해보세요 🍃',
              ),
            ),

            const SizedBox(height: 15),

            // 🔹 명상하기 카드 (✅ MeditationPage로 이동)
            GestureDetector(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const MeditationPage()),
                );
              },
              child: _activityCard(
                color: Colors.blue[50]!,
                icon: Icons.self_improvement,
                title: '명상하기',
                subtitle: '마음을 비우고 호흡에 집중해보세요 🧘‍♀️',
              ),
            ),

            const SizedBox(height: 15),

            // 🔹 미니게임 카드
            GestureDetector(
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('미니게임 기능 준비 중 🎮')),
                );
              },
              child: _activityCard(
                color: Colors.orange[50]!,
                icon: Icons.sports_esports,
                title: '스트레스 해소 미니게임',
                subtitle: '간단한 두더지 잡기나 클릭 게임으로 기분 전환!',
              ),
            ),
          ],
        ),
      ),
      // ✅ 하단 탭 추가
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: Colors.white,
        selectedItemColor: const Color(0xFF3B82F6),
        unselectedItemColor: Colors.grey,
        currentIndex: 2, // 스트레스 해소 탭
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: '홈'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: '마이페이지'),
          BottomNavigationBarItem(icon: Icon(Icons.spa_outlined), label: '스트레스 해소'),
        ],
        onTap: (index) => _onBottomTap(context, index),
      ),
    );
  }

  Widget _activityCard({
    required Color color,
    required IconData icon,
    required String title,
    required String subtitle,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      padding: const EdgeInsets.all(18),
      child: Row(
        children: [
          Icon(icon, size: 40, color: Colors.black54),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(
                        fontSize: 17, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(subtitle,
                    style: const TextStyle(fontSize: 14, color: Colors.black54)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
