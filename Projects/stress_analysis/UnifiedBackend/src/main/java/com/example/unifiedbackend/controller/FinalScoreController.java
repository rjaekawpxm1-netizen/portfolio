package com.example.unifiedbackend.controller;

import com.example.unifiedbackend.entity.Score;
import com.example.unifiedbackend.repository.ScoreRepository;
import com.example.unifiedbackend.service.ScoreService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

@RestController
@RequestMapping("/api/final")
@CrossOrigin
public class FinalScoreController {

    private final ScoreRepository scoreRepository;
    private final ScoreService scoreService;

    public FinalScoreController(ScoreRepository scoreRepository, ScoreService scoreService) {
        this.scoreRepository = scoreRepository;
        this.scoreService = scoreService;
    }

    @PostMapping("/calculate")
    public ResponseEntity<Map<String, Object>> calculateFinalScore(@RequestParam("scoreId") Long scoreId) {
        Score score = scoreRepository.findById(scoreId).orElse(null);
        if (score == null) {
            return ResponseEntity.status(404).body(Map.of("error", "Score not found"));
        }

        double weighted = (score.getFaceScore() * 0.4)
                + (score.getVoiceScore() * 0.4)
                + (score.getQuestionScore() * 0.2);
        int finalScore = (int) Math.round(weighted);

        String emotion = determineEmotion(finalScore);
        RecommendationResult result = callPythonRecommendation(emotion);
        String solution = getRandomSolution(emotion);

        scoreService.updateFinalRecommendation(
                scoreId,
                finalScore,
                result.recommendedSongs,
                emotion,
                result.recommendedMovie,
                result.moviePosterUrl,
                result.movieRatingPercent,
                solution
        );

        Map<String, Object> response = new HashMap<>();
        response.put("finalScore", finalScore);
        response.put("emotion", emotion);
        response.put("recommendedSongs", result.recommendedSongs);
        response.put("recommendedMovie", result.recommendedMovie);
        response.put("moviePosterUrl", result.moviePosterUrl);
        response.put("movieRatingPercent", result.movieRatingPercent);
        response.put("solution", solution);

        return ResponseEntity.ok(response);
    }

    private String determineEmotion(int score) {
        if (score >= 75) return "Anger";
        else if (score >= 50) return "Anxiety";
        else if (score >= 25) return "Sadness";
        else return "Normal";
    }

    private String getRandomSolution(String emotion) {
        Map<String, List<String>> emotionMessages = Map.of(
                "Anger", List.of(
                        "🔥 깊게 숨을 들이쉬고, 잠시 자리를 벗어나 보세요.",
                        "💢 산책이나 가벼운 운동으로 마음을 풀어보세요.",
                        "🌿 지금 느끼는 분노는 자연스러운 감정이에요. 천천히 가라앉힐 수 있어요.",
                        "💧 따뜻한 물로 샤워하며 몸과 마음을 진정시켜보세요.",
                        "☕ 좋아하는 음료 한 잔으로 잠시 여유를 가져보세요.",
                        "🎧 음악을 들으며 기분을 환기해보세요."
                ),
                "Anxiety", List.of(
                        "🌿 명상이나 호흡 운동으로 마음의 긴장을 풀어보세요.",
                        "💭 불안한 마음은 당신이 진지하게 노력하고 있다는 증거예요.",
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

    private RecommendationResult callPythonRecommendation(String emotion) {
        try {
            ProcessBuilder pb = new ProcessBuilder(
                    "python.exe",
                    "C:/Users/Huni/Desktop/Cap/UnifiedBackend/scripts/recommend_songs.py",
                    emotion
            );
            pb.redirectErrorStream(true);
            Process process = pb.start();
            process.waitFor();

            BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8)
            );

            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
            reader.close();

            String[] lines = output.toString().trim().split("\n");

            String recommendedSongs = lines.length > 0 ? lines[0].trim().replace("\\n", "\n") : "";
            String recommendedMovie = lines.length > 1 ? lines[1].trim() : "";
            String moviePosterUrl = lines.length > 2 ? lines[2].trim() : "";
            int ratingPercent = 0;

            if (lines.length > 3) {
                try {
                    ratingPercent = Integer.parseInt(lines[3].trim());
                } catch (NumberFormatException e) {
                    System.out.println("평점 파싱 실패: " + lines[3]);
                }
            }

            return new RecommendationResult(recommendedSongs, recommendedMovie, moviePosterUrl, ratingPercent);

        } catch (Exception e) {
            e.printStackTrace();
            return new RecommendationResult("추천 실패", "추천 실패", "", 0);
        }
    }

    static class RecommendationResult {
        String recommendedSongs;
        String recommendedMovie;
        String moviePosterUrl;
        int movieRatingPercent;

        RecommendationResult(String songs, String movie, String poster, int ratingPercent) {
            this.recommendedSongs = songs;
            this.recommendedMovie = movie;
            this.moviePosterUrl = poster;
            this.movieRatingPercent = ratingPercent;
        }
    }

    @GetMapping("/get")
    public ResponseEntity<Map<String, Object>> getFinalScore(@RequestParam("scoreId") Long scoreId) {
        Score score = scoreRepository.findById(scoreId).orElse(null);
        if (score == null) {
            return ResponseEntity.status(404).body(Map.of("error", "Score not found"));
        }

        Map<String, Object> response = new HashMap<>();
        response.put("finalScore", score.getFinalScore());
        response.put("emotion", score.getEmotion());
        response.put("recommendedSongs", score.getRecommendedSongs());
        response.put("recommendedMovie", score.getRecommendedMovie());
        response.put("moviePosterUrl", score.getMoviePosterUrl());
        response.put("movieRatingPercent", score.getMovieRatingPercent());
        response.put("solution", score.getSolution());
        return ResponseEntity.ok(response);
    }
}
