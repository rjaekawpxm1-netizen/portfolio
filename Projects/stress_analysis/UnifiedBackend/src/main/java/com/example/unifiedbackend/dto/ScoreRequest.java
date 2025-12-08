package com.example.unifiedbackend.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ScoreRequest {
    
    private String email;              // 사용자 이메일
    private double faceScore;          // 얼굴 기반 점수
    private double voiceScore;         // 음성 기반 점수
    private double questionScore;      // 질문 응답 기반 점수
    private int finalScore;            // 최종 종합 점수
    private String emotion;            // 감정 분류 (Anger, Sadness 등)
    private String recommendedSongs;   // 추천된 노래 리스트 (줄바꿈 포함 문자열)
    private boolean favorite;          // 즐겨찾기 여부
}
