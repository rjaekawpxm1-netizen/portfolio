package com.example.unifiedbackend.controller;

import com.example.unifiedbackend.entity.Record;
import com.example.unifiedbackend.repository.RecordRepository;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import java.util.*;

@RestController
@RequestMapping("/api/records")
@CrossOrigin
public class RecordController {

    private final RecordRepository recordRepository;

    public RecordController(RecordRepository recordRepository) {
        this.recordRepository = recordRepository;
    }

    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> getRecordsByEmail(@RequestParam("email") String email) {
        List<Record> records = recordRepository.findByEmail(email);
        records.sort(Comparator.comparing(Record::getCreatedAt));
        return ResponseEntity.ok(convertToResponse(records));
    }

    @DeleteMapping("/{recordId}")
    public ResponseEntity<String> deleteRecord(@PathVariable Long recordId) {
        if (!recordRepository.existsById(recordId)) {
            return ResponseEntity.notFound().build();
        }
        recordRepository.deleteById(recordId);
        return ResponseEntity.ok("삭제 완료");
    }

    @PatchMapping("/{recordId}/favorite")
    public ResponseEntity<Record> updateFavorite(@PathVariable Long recordId, @RequestBody Map<String, Boolean> payload) {
        boolean newFavorite = payload.getOrDefault("favorite", false);
        Record record = recordRepository.findById(recordId)
                .orElseThrow(() -> new RuntimeException("recordId not found"));
        record.setFavorite(newFavorite);
        return ResponseEntity.ok(recordRepository.save(record));
    }

    @GetMapping("/all")
    public List<Record> getAllRecords() {
        return recordRepository.findAll();
    }

    @GetMapping("/favorites")
    public ResponseEntity<List<Map<String, Object>>> getFavoriteRecords(@RequestParam(value = "email", required = false) String email) {
        List<Record> records;
        if (email != null && !email.isEmpty()) {
            records = recordRepository.findByEmailAndFavoriteTrue(email);
        } else {
            records = recordRepository.findByFavoriteTrue();
        }
        records.sort(Comparator.comparing(Record::getCreatedAt).reversed());
        return ResponseEntity.ok(convertToResponse(records));
    }

    @GetMapping("/latest")
    public ResponseEntity<Map<String, Object>> getLatestRecord(@RequestParam("email") String email) {
        List<Record> records = recordRepository.findByEmail(email);
        if (records.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        records.sort(Comparator.comparing(Record::getCreatedAt).reversed());
        Record latest = records.get(0);

        Map<String, Object> map = new HashMap<>();
        map.put("id", latest.getId());
        map.put("finalScore", latest.getFinalScore());
        map.put("emotion", latest.getEmotionResult());
        map.put("recommendedSongs", latest.getRecommendedSongs());
        map.put("recommendedMovie", latest.getRecommendedMovie());
        map.put("reason", latest.getReason());
        map.put("solution", latest.getSolution());
        map.put("createdAt", latest.getCreatedAt());
        map.put("favorite", latest.isFavorite());
        map.put("moviePosterUrl", latest.getMoviePosterUrl());
        map.put("movieRatingPercent", latest.getMovieRatingPercent());

        return ResponseEntity.ok(map);
    }

    private List<Map<String, Object>> convertToResponse(List<Record> records) {
        List<Map<String, Object>> result = new ArrayList<>();
        for (Record record : records) {
            Map<String, Object> map = new HashMap<>();
            map.put("id", record.getId());
            map.put("finalScore", record.getFinalScore());
            map.put("emotion", record.getEmotionResult());
            map.put("recommendedSongs", record.getRecommendedSongs());
            map.put("recommendedMovie", record.getRecommendedMovie());
            map.put("reason", record.getReason());
            map.put("solution", record.getSolution());
            map.put("createdAt", record.getCreatedAt());
            map.put("favorite", record.isFavorite());
            map.put("moviePosterUrl", record.getMoviePosterUrl());
            map.put("movieRatingPercent", record.getMovieRatingPercent());
            result.add(map);
        }
        return result;
    }
}
