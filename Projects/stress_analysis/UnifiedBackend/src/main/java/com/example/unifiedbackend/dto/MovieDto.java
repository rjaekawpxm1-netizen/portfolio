package com.example.unifiedbackend.dto;

public class MovieDto {
    private String title;
    private String posterUrl;
    private String overview;
    private int ratingPercent; // 평점을 퍼센트로

    public MovieDto(String title, String posterUrl, String overview, double voteAverage) {
        this.title = title;
        this.posterUrl = posterUrl;
        this.overview = overview;
        this.ratingPercent = (int) Math.round(voteAverage * 10);  // ★ 퍼센트로 변환
    }

    public String getTitle() { return title; }
    public String getPosterUrl() { return posterUrl; }
    public String getOverview() { return overview; }
    public int getRatingPercent() { return ratingPercent; }
}
