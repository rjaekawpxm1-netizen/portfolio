package com.example.unifiedbackend.controller;

import com.example.unifiedbackend.entity.Score;
import com.example.unifiedbackend.repository.ScoreRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/score")
@CrossOrigin
public class SessionController {

    private final ScoreRepository scoreRepository;

    public SessionController(ScoreRepository scoreRepository) {
        this.scoreRepository = scoreRepository;
    }

    @PostMapping("/new")
    public ResponseEntity<Score> createNewSession() {
        Score score = new Score(); // 빈 Score 생성
        scoreRepository.save(score);
        return ResponseEntity.ok(score);
    }
}
