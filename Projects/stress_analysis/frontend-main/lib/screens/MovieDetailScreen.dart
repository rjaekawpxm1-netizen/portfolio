// lib/screens/movie_detail_screen.dart

import 'package:flutter/material.dart';
import '../models/movie.dart';
import 'package:cached_network_image/cached_network_image.dart';

class MovieDetailScreen extends StatelessWidget {
  final Movie movie;

  const MovieDetailScreen({super.key, required this.movie});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(movie.title),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            CachedNetworkImage(
              imageUrl: movie.posterUrl,
              fit: BoxFit.cover,
              width: double.infinity,
              errorWidget: (context, url, error) => const Icon(Icons.image_not_supported),
            ),
            const SizedBox(height: 16),
            Text(
              movie.title,
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Text(
              movie.overview.isNotEmpty
                  ? movie.overview
                  : '해당 영화에 대한 상세 정보가 부족합니다.',
              style: const TextStyle(fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}
