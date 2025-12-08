package com.example.unifiedbackend.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
public class Score {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "user_id")
    private User user;

    private Double faceScore;
    private Double voiceScore;
    private Double questionScore;
    private Integer finalScore;

    @Column(length = 1000)
    private String recommendedSongs; // 추천곡 결과 저장용

    @Column(length = 50)
    private String emotion; // 감정 분류 결과 저장용

    @Column(nullable = false)
    private boolean favorite = false;

    @Column(length = 500)
    private String solution;  // 해결방안 추천 문구

    @Column(length = 300)
    private String recommendedMovie; // 추천 영화 제목

    @Column(length = 1000)
    private String moviePosterUrl; // 영화 포스터 이미지 URL

    // ⭐️ 추가: TMDB 평점 (%)
    @Column
    private Integer movieRatingPercent; // 영화 평점 (0~100%)

    private LocalDateTime createdAt = LocalDateTime.now();
}
