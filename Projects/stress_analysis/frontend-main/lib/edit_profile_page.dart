import 'package:flutter/material.dart';

class EditProfilePage extends StatelessWidget {
  const EditProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    final nameController = TextEditingController();
    final emailController = TextEditingController();

    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF3B82F6), // 파란색 배경
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white), // 흰색 아이콘
          onPressed: () {
            Navigator.pop(context); // 뒤로가기
          },
        ),
        centerTitle: true,
        title: const Text(
          '개인정보 변경',
          style: TextStyle(fontSize: 16, color: Colors.white), // 흰색 텍스트
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 60),
              TextField(
                controller: nameController,
                decoration: const InputDecoration(labelText: '이름'),
              ),
              const SizedBox(height: 20),
              TextField(
                controller: emailController,
                decoration: const InputDecoration(labelText: '이메일'),
              ),
              const SizedBox(height: 40),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF3B82F6), // 파란색 버튼
                  ),
                  onPressed: () {
                    // 저장 로직 구현
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('저장되었습니다.')),
                    );
                    Navigator.pop(context); // 이전 페이지로
                  },
                  child: const Text(
                    '저장',
                    style: TextStyle(color: Colors.white), // 흰색 텍스트
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
