package com.example.unifiedbackend.controller;

import com.example.unifiedbackend.dto.MovieDto;
import com.example.unifiedbackend.entity.Score;
import com.example.unifiedbackend.entity.User;
import com.example.unifiedbackend.repository.ScoreRepository;
import com.example.unifiedbackend.repository.UserRepository;
import com.example.unifiedbackend.service.MovieService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.time.LocalDateTime;
import java.util.*;

@RestController
@RequestMapping("/api/scores")
@CrossOrigin
public class ScoreController {

    private final ScoreRepository scoreRepository;
    private final UserRepository userRepository;
    private final MovieService movieService;

    public ScoreController(ScoreRepository scoreRepository, UserRepository userRepository, MovieService movieService) {
        this.scoreRepository = scoreRepository;
        this.userRepository = userRepository;
        this.movieService = movieService;
    }

    @PostMapping("/init")
    public ResponseEntity<?> initScore(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        if (email == null || email.isEmpty()) {
            return ResponseEntity.badRequest().body("이메일 누락");
        }

        User user = userRepository.findByEmail(email).orElse(null);
        if (user == null) {
            return ResponseEntity.badRequest().body("사용자 없음");
        }

        Score score = new Score();
        score.setUser(user);
        score.setCreatedAt(LocalDateTime.now());
        scoreRepository.save(score);

        return ResponseEntity.ok(score.getId());
    }

    @PostMapping("/recommend")
    public ResponseEntity<?> recommendSongs(@RequestBody Map<String, Long> request) {
        Long scoreId = request.get("scoreId");
        if (scoreId == null) {
            return ResponseEntity.badRequest().body("scoreId 누락");
        }

        Score score = scoreRepository.findById(scoreId).orElse(null);
        if (score == null) {
            return ResponseEntity.badRequest().body("Score ID 없음");
        }

        Double voice = score.getVoiceScore();
        Double face = score.getFaceScore();

        if (voice == null || face == null) {
            return ResponseEntity.badRequest().body("voiceScore 또는 faceScore 없음");
        }

        int finalScore = (int) Math.round((voice + face) / 2.0);
        String emotion;
        if (finalScore >= 85) emotion = "Anger";
        else if (finalScore >= 70) emotion = "Anxiety";
        else if (finalScore >= 50) emotion = "Sadness";
        else emotion = "Normal";

        try {
            ProcessBuilder pb = new ProcessBuilder(
                    "python",
                    "C:/Users/Huni/Desktop/Cap/UnifiedBackend/scripts/recommend_songs.py",
                    emotion
            );
            Process process = pb.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }

            String recommendedSongs = output.toString().trim();
            List<MovieDto> movies = movieService.getRecommendedMovies(emotion, 1);
            MovieDto movie = !movies.isEmpty() ? movies.get(0) : null;
            String solution = getRandomSolution(emotion);

            score.setFinalScore(finalScore);
            score.setEmotion(emotion);
            score.setRecommendedSongs(recommendedSongs);
            score.setSolution(solution);

            if (movie != null) {
                score.setRecommendedMovie(movie.getTitle());
                score.setMoviePosterUrl(movie.getPosterUrl());
                score.setMovieRatingPercent(movie.getRatingPercent());
            }

            scoreRepository.save(score);

            Map<String, Object> result = new HashMap<>();
            result.put("emotion", emotion);
            result.put("finalScore", finalScore);
            result.put("songs", recommendedSongs);
            result.put("solution", solution);
            if (movie != null) {
                result.put("movieTitle", movie.getTitle());
                result.put("moviePosterUrl", movie.getPosterUrl());
                result.put("movieRatingPercent", movie.getRatingPercent());
                result.put("movieOverview", movie.getOverview());
            }

            return ResponseEntity.ok(result);

        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("추천 실패: " + e.getMessage());
        }
    }

    private String getRandomSolution(String emotion) {
        Map<String, List<String>> emotionMessages = Map.of(
                "Anger", List.of(
                        "🔥 깊게 숨을 들이쉬고 잠시 자리를 벗어나 보세요.",
                        "💢 산책이나 가벼운 운동으로 마음을 풀어보세요.",
                        "🌿 지금의 분노는 자연스러운 감정이에요. 천천히 가라앉힐 수 있어요.",
                        "💧 따뜻한 물로 샤워하며 몸과 마음을 진정시켜보세요.",
                        "☕ 좋아하는 음료 한 잔으로 잠시 여유를 가져보세요.",
                        "🎧 음악을 들으며 기분을 환기해보세요."
                ),
                "Anxiety", List.of(
                        "🌿 명상이나 호흡 운동으로 마음의 긴장을 풀어보세요.",
                        "💭 불안은 당신이 진심으로 노력하고 있다는 증거예요.",
                        "☕ 따뜻한 차 한 잔과 함께 천천히 숨을 고르세요.",
                        "🌤️ 오늘은 조금 천천히 살아도 괜찮아요.",
                        "💬 지금의 불안은 영원하지 않아요. 곧 괜찮아질 거예요.",
                        "🕊️ 걱정이 많을 땐 작은 일부터 하나씩 해보세요."
                ),
                "Sadness", List.of(
                        "💧 감정을 억누르지 말고 그대로 느껴보세요. 그것도 치유의 시작이에요.",
                        "🎶 좋아하는 음악을 들으며 마음을 달래보세요.",
                        "💬 누군가에게 솔직하게 털어놓는 것도 큰 도움이 될 거예요.",
                        "🌙 슬픔은 당신이 깊이 느낄 줄 아는 사람이라는 증거예요.",
                        "☀️ 따뜻한 햇살을 쬐며 스스로를 다독여주세요.",
                        "🌷 오늘은 자신에게 조금 더 따뜻하게 대해주세요."
                ),
                "Normal", List.of(
                        "🌤️ 오늘의 평온함을 소중히 간직하세요.",
                        "🌱 지금의 안정된 마음이 내일의 힘이 될 거예요.",
                        "☀️ 하루를 잘 보내고 있는 당신, 정말 멋져요.",
                        "🌻 감사한 마음으로 자신을 칭찬해보세요.",
                        "🍀 지금처럼 천천히, 편안하게 하루를 이어가세요.",
                        "🌈 이 평온한 기분이 자주 찾아오길 바라요."
                )
        );

        List<String> messages = emotionMessages.getOrDefault(
                emotion,
                List.of("🌸 오늘도 충분히 잘하고 있어요.", "🌼 지금 이 순간을 있는 그대로 받아들이세요.")
        );
        return messages.get(new Random().nextInt(messages.size()));
    }
}
