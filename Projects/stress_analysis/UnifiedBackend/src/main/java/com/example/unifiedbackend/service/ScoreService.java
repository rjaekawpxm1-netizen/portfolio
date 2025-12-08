package com.example.unifiedbackend.service;

import com.example.unifiedbackend.entity.Record;
import com.example.unifiedbackend.entity.Score;
import com.example.unifiedbackend.repository.RecordRepository;
import com.example.unifiedbackend.repository.ScoreRepository;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;

@Service
public class ScoreService {

    private final ScoreRepository scoreRepository;
    private final RecordRepository recordRepository;

    public ScoreService(ScoreRepository scoreRepository, RecordRepository recordRepository) {
        this.scoreRepository = scoreRepository;
        this.recordRepository = recordRepository;
    }

    public Score updateFaceScore(Long scoreId, double score) {
        Score s = scoreRepository.findById(scoreId)
                .orElseThrow(() -> new RuntimeException("scoreId not found"));
        s.setFaceScore(score);
        return scoreRepository.save(s);
    }

    public Score updateVoiceScore(Long scoreId, double score) {
        Score s = scoreRepository.findById(scoreId)
                .orElseThrow(() -> new RuntimeException("scoreId not found"));
        s.setVoiceScore(score);
        return scoreRepository.save(s);
    }

    public Score updateQuestionScore(Long scoreId, double score) {
        Score s = scoreRepository.findById(scoreId)
                .orElseThrow(() -> new RuntimeException("scoreId not found"));
        s.setQuestionScore(score);
        return scoreRepository.save(s);
    }

    public Score updateFinalScore(Long scoreId, int score) {
        Score s = scoreRepository.findById(scoreId)
                .orElseThrow(() -> new RuntimeException("scoreId not found"));
        s.setFinalScore(score);
        return scoreRepository.save(s);
    }

    public Score updateFinalScoreAndSongs(Long scoreId, int finalScore, String recommendedSongs) {
        Score s = scoreRepository.findById(scoreId)
                .orElseThrow(() -> new RuntimeException("scoreId not found"));
        s.setFinalScore(finalScore);
        s.setRecommendedSongs(recommendedSongs);
        return scoreRepository.save(s);
    }

    public Score updateFinalScoreAndSongs(Long scoreId, int finalScore, String recommendedSongs, String emotion) {
        Score s = scoreRepository.findById(scoreId)
                .orElseThrow(() -> new RuntimeException("scoreId not found"));
        s.setFinalScore(finalScore);
        s.setRecommendedSongs(recommendedSongs);
        s.setEmotion(emotion);
        return scoreRepository.save(s);
    }

    public Score updateFinalRecommendation(
            Long scoreId,
            int finalScore,
            String recommendedSongs,
            String emotion,
            String movieTitle,
            String posterUrl,
            int movieRatingPercent,
            String solution
    ) {
        Score s = scoreRepository.findById(scoreId)
                .orElseThrow(() -> new RuntimeException("scoreId not found"));

        s.setFinalScore(finalScore);
        s.setRecommendedSongs(recommendedSongs);
        s.setEmotion(emotion);
        s.setRecommendedMovie(movieTitle);
        s.setMoviePosterUrl(posterUrl);
        s.setMovieRatingPercent(movieRatingPercent);
        s.setSolution(solution);
        scoreRepository.save(s);

        try {
            Record record = new Record();
            String email = (s.getUser() != null && s.getUser().getEmail() != null)
                    ? s.getUser().getEmail()
                    : "rlaxogns199@example.com";

            record.setEmail(email);
            record.setFinalScore(finalScore);
            record.setEmotionResult(emotion);
            record.setRecommendedSongs(recommendedSongs);
            record.setRecommendedMovie(movieTitle);
            record.setMoviePosterUrl(posterUrl);
            record.setMovieRatingPercent(movieRatingPercent);
            record.setSolution(solution);
            record.setCreatedAt(LocalDateTime.now());
            record.setFavorite(false);
            record.setScoreId(scoreId);

            recordRepository.save(record);
            System.out.println("✅ Record 저장 완료: " + email);
        } catch (Exception e) {
            System.out.println("⚠️ Record 저장 실패: " + e.getMessage());
        }

        return s;
    }
}
