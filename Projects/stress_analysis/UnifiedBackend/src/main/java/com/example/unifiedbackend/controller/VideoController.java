package com.example.unifiedbackend.controller;

import com.example.unifiedbackend.service.ScoreService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

@RestController
@RequestMapping("/api")
public class VideoController {

    private final ScoreService scoreService;

    public VideoController(ScoreService scoreService) {
        this.scoreService = scoreService;
    }

    @PostMapping("/video")
    public ResponseEntity<String> handleVideoUpload(
            @RequestParam("file") MultipartFile file,
            @RequestParam("scoreId") Long scoreId
    ) {
        String savePath = "C:/Users/Huni/Desktop/Cap/UnifiedBackend/scripts/video.mp4";
        savePath = savePath.replace("\\", "/");

        try {
            // 1️⃣ 파일 저장
            Files.copy(file.getInputStream(), Paths.get(savePath), StandardCopyOption.REPLACE_EXISTING);
            System.out.println("✅ 파일 저장 완료");

            // 2️⃣ 파이썬 실행
            ProcessBuilder pb = new ProcessBuilder(
                    "C:/Users/Huni/AppData/Local/Programs/Python/Python310/python.exe",
                    "C:/Users/Huni/Desktop/Cap/UnifiedBackend/scripts/predict_emotion_from_video.py",
                    savePath
            );
            pb.redirectErrorStream(true);
            Process process = pb.start();

            // 3️⃣ 파이썬 출력 읽기 (UTF-8로 명시)
            BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8)
            );

            String line;
            String lastLine = null;

            while ((line = reader.readLine()) != null) {
                System.out.println("파이썬 출력: " + line);
                lastLine = line.trim(); // 마지막 줄 저장
            }

            int exitCode = process.waitFor();
            System.out.println("✅ Python 종료 코드: " + exitCode);
            System.out.println("✅ 최종 점수 라인: " + lastLine);

            // 4️⃣ 파이썬 출력 없을 경우 기본값 처리
            double score = 0.0;
            if (lastLine != null && !lastLine.isEmpty()) {
                try {
                    score = Double.parseDouble(lastLine);
                } catch (NumberFormatException ex) {
                    System.err.println("⚠️ 파이썬 출력 파싱 실패: " + lastLine);
                }
            } else {
                System.err.println("⚠️ 파이썬 출력이 비어 있음");
            }

            System.out.println("✅ 최종 점수(double): " + score);

            // 5️⃣ DB 업데이트
            scoreService.updateFaceScore(scoreId, score);
            System.out.println("✅ faceScore 업데이트 완료");

            // 6️⃣ 임시 파일 삭제
            Files.deleteIfExists(Paths.get(savePath));
            System.out.println("✅ 영상 파일 삭제 완료");

            return ResponseEntity.ok("업데이트 성공 (점수: " + score + ")");
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }
}
