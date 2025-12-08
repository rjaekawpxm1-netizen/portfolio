package com.example.unifiedbackend.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.time.LocalDateTime;

@Getter
@Setter
@Entity
public class Record {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String email;

    private String emotionResult;

    @Column(length = 1000)
    private String recommendedSongs;

    @Column(length = 300)
    private String recommendedMovie;

    @Column(length = 500)
    private String reason;

    @Column(length = 500)
    private String solution;

    private LocalDateTime createdAt;

    @Column(nullable = false)
    private boolean favorite = false;

    @Column(length = 1000)
    private String moviePosterUrl;

    @Column
    private Integer movieRatingPercent;

    @Column
    private Integer finalScore;

    @Column
    private Long scoreId;
}
