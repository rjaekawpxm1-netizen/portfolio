package com.example.unifiedbackend.repository;

import com.example.unifiedbackend.entity.Score;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ScoreRepository extends JpaRepository<Score, Long> {
    Score findTopByOrderByIdDesc();  // 전체 최신 Score (관리용)
    Score findTopByUser_EmailOrderByIdDesc(String email);  // 특정 사용자 최신 Score
}
