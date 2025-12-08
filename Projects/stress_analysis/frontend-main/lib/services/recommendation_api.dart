import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/movie.dart';

class RecommendationApi {
  static const String baseUrl = 'http://10.0.2.2:8080';

  Future<List<Movie>> fetchMoviesByEmotion(String emotion, {int count = 2}) async {
    final uri = Uri.parse('$baseUrl/api/recommendations/movies?emotion=$emotion&count=$count');
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      final List<dynamic> decoded = json.decode(response.body);
      return decoded.map((e) => Movie.fromJson(e)).toList();
    } else {
      throw Exception('영화 추천 API 요청 실패: ${response.statusCode}');
    }
  }
}
