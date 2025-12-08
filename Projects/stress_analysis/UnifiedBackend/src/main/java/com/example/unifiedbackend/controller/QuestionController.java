package com.example.unifiedbackend.controller;

import com.example.unifiedbackend.entity.Score;
import com.example.unifiedbackend.service.ScoreService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/question")
@CrossOrigin
public class QuestionController {

    @Autowired
    private ScoreService scoreService;


    @PostMapping("/submit")
    public ResponseEntity<Score> submitQuestionScore(
            @RequestParam("score") double score,
            @RequestParam("scoreId") Long scoreId
    ) {
        Score updatedScore = scoreService.updateQuestionScore(scoreId, score);
        return ResponseEntity.ok(updatedScore);
    }
}
