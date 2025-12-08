package com.example.unifiedbackend.controller;

import com.example.unifiedbackend.entity.Score;
import com.example.unifiedbackend.repository.ScoreRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.*;

@RestController
@RequestMapping("/api")
@CrossOrigin
public class AudioController {

    private final ScoreRepository scoreRepository;

    public AudioController(ScoreRepository scoreRepository) {
        this.scoreRepository = scoreRepository;
    }

    @PostMapping("/audio")
    public ResponseEntity<String> handleAudioUpload(
            @RequestParam("file") MultipartFile file,
            @RequestParam("scoreId") Long scoreId
    ) {
        String savePath = "C:/Users/Huni/Desktop/Cap/UnifiedBackend/scripts/audio.wav";
        savePath = savePath.replace("\\", "/");

        try {
            // 1️⃣ 파일 저장
            Files.copy(file.getInputStream(), Paths.get(savePath), StandardCopyOption.REPLACE_EXISTING);
            System.out.println("✅ 오디오 파일 저장 완료");

            // 2️⃣ scoreId로 기존 row 가져오기
            Score existingScore = scoreRepository.findById(scoreId).orElse(null);
            if (existingScore == null) {
                return ResponseEntity.badRequest().body("해당 scoreId 없음");
            }

            // 3️⃣ 파이썬 실행 (여기서 음성 모델 실행)
            ProcessBuilder pb = new ProcessBuilder(
                    "C:/Users\\Huni/AppData/Local/Programs/Python/Python310/python.exe",
                    "C:/Users/Huni/Desktop/Cap/UnifiedBackend/scripts/predict_emotion_from_audio.py",
                    savePath
            );
            pb.redirectErrorStream(true);
            Process process = pb.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String scoreStr;
            String lastLine = null;

            while ((scoreStr = reader.readLine()) != null) {
                System.out.println("파이썬 출력: " + scoreStr);
                lastLine = scoreStr;
            }

            if (lastLine == null) {
                throw new IllegalStateException("파이썬에서 점수를 반환하지 않았습니다.");
            }

            double voiceScore = Double.parseDouble(lastLine.trim());
            System.out.println("✅ 최종 음성 점수: " + voiceScore);

            // 4️⃣ 해당 row에 음성 점수 업데이트
            existingScore.setVoiceScore(voiceScore);
            scoreRepository.save(existingScore);
            System.out.println("✅ voiceScore 업데이트 완료");

            // 5️⃣ 파일 삭제
            Files.deleteIfExists(Paths.get(savePath));
            System.out.println("✅ 오디오 파일 삭제 완료");

            return ResponseEntity.ok("업데이트 성공");
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }
}
