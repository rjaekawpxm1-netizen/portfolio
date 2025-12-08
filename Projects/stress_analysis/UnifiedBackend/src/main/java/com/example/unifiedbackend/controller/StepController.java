package com.example.unifiedbackend.controller;

import com.example.unifiedbackend.entity.StepRecord;
import com.example.unifiedbackend.repository.StepRecordRepository;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import java.time.LocalDateTime;
import java.util.*;

@RestController
@RequestMapping("/api/steps")
@CrossOrigin
public class StepController {

    private final StepRecordRepository stepRecordRepository;

    public StepController(StepRecordRepository stepRecordRepository) {
        this.stepRecordRepository = stepRecordRepository;
    }

    @PostMapping("/save")
    public ResponseEntity<String> saveSteps(@RequestBody Map<String, Object> payload) {
        String email = (String) payload.get("email");
        int steps = ((Number) payload.get("steps")).intValue();

        StepRecord record = new StepRecord();
        record.setEmail(email);
        record.setSteps(steps);
        record.setDate(LocalDateTime.now());

        stepRecordRepository.save(record);
        return ResponseEntity.ok("걸음 수 저장 완료");
    }

    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> getStepsByEmail(@RequestParam String email) {
        List<StepRecord> records = stepRecordRepository.findByEmailOrderByDateDesc(email);
        List<Map<String, Object>> result = new ArrayList<>();

        for (StepRecord r : records) {
            Map<String, Object> map = new HashMap<>();
            map.put("id", r.getId());
            map.put("email", r.getEmail());
            map.put("steps", r.getSteps());
            map.put("date", r.getDate());
            result.add(map);
        }
        return ResponseEntity.ok(result);
    }

    @GetMapping("/latest")
    public ResponseEntity<Map<String, Object>> getLatestStep(@RequestParam String email) {
        List<StepRecord> records = stepRecordRepository.findByEmailOrderByDateDesc(email);
        if (records.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        StepRecord latest = records.get(0);
        Map<String, Object> map = new HashMap<>();
        map.put("id", latest.getId());
        map.put("email", latest.getEmail());
        map.put("steps", latest.getSteps());
        map.put("date", latest.getDate());

        return ResponseEntity.ok(map);
    }
}
