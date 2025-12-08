package com.example.unifiedbackend.controller;

import com.example.unifiedbackend.dto.AuthRequest;
import com.example.unifiedbackend.dto.ChangePasswordRequest;
import com.example.unifiedbackend.entity.User;
import com.example.unifiedbackend.service.AuthService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*", allowedHeaders = "*")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    // ✅ 회원가입
    @PostMapping("/signup")
    public ResponseEntity<Map<String, Object>> signup(@RequestBody AuthRequest request) {
        Map<String, Object> response = new HashMap<>();
        if (authService.signup(request)) {
            response.put("status", "success");
            response.put("message", "회원가입 성공");
            return ResponseEntity.ok(response);
        } else {
            response.put("status", "fail");
            response.put("message", "이미 존재하는 이메일입니다.");
            return ResponseEntity.badRequest().body(response);
        }
    }

    // ✅ 로그인
    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody AuthRequest request) {
        Map<String, Object> response = new HashMap<>();
        if (authService.login(request)) {
            response.put("status", "success");
            response.put("message", "로그인 성공");
            response.put("email", request.getEmail());
            return ResponseEntity.ok(response);
        } else {
            response.put("status", "fail");
            response.put("message", "로그인 실패: 이메일 또는 비밀번호가 올바르지 않습니다.");
            return ResponseEntity.status(401).body(response);
        }
    }

    // ✅ 비밀번호 변경
    @PostMapping("/change-password")
    public ResponseEntity<Map<String, String>> changePassword(@RequestBody ChangePasswordRequest request) {
        Map<String, String> response = new HashMap<>();
        if (authService.changePassword(request)) {
            response.put("message", "비밀번호 변경 성공");
            return ResponseEntity.ok(response);
        } else {
            response.put("message", "비밀번호 변경 실패: 현재 비밀번호 불일치 또는 사용자 없음");
            return ResponseEntity.badRequest().body(response);
        }
    }

    // ✅ 이메일 찾기 (이름으로)
    @GetMapping("/find-email")
    public ResponseEntity<Map<String, Object>> findEmailByName(@RequestParam String name) {
        Optional<String> email = authService.findEmailByName(name);
        Map<String, Object> response = new HashMap<>();

        if (email.isPresent()) {
            response.put("email", email.get());
            return ResponseEntity.ok(response);
        } else {
            response.put("message", "해당 이름의 사용자를 찾을 수 없습니다.");
            return ResponseEntity.status(404).body(response);
        }
    }

    // ✅ 이름 + 전화번호로 이메일 여러 개 찾기
    @GetMapping("/find-emails")
    public ResponseEntity<Map<String, Object>> findEmailsByNameAndPhone(
            @RequestParam String name,
            @RequestParam String phone) {

        List<String> emails = authService.findEmailsByNameAndPhone(name, phone);
        Map<String, Object> response = new HashMap<>();

        if (emails.isEmpty()) {
            response.put("message", "해당 정보의 사용자를 찾을 수 없습니다.");
            return ResponseEntity.status(404).body(response);
        } else {
            response.put("emails", emails);
            return ResponseEntity.ok(response);
        }
    }

    // ✅ 인증 코드 전송
    @PostMapping("/send-verification-code")
    public ResponseEntity<Map<String, String>> sendVerificationCode(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        Map<String, String> response = new HashMap<>();

        if (email == null || email.isEmpty()) {
            response.put("message", "이메일을 입력해주세요.");
            return ResponseEntity.badRequest().body(response);
        }

        if (authService.sendVerificationCode(email)) {
            String code = authService.getVerificationCode(email);
            response.put("message", "인증 코드가 발송되었습니다.");
            response.put("code", code);
            return ResponseEntity.ok(response);
        } else {
            response.put("message", "해당 이메일의 사용자를 찾을 수 없습니다.");
            return ResponseEntity.status(404).body(response);
        }
    }

    // ✅ 비밀번호 재설정
    @PostMapping("/reset-password")
    public ResponseEntity<Map<String, String>> resetPassword(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String code = request.get("code");
        String newPassword = request.get("newPassword");
        Map<String, String> response = new HashMap<>();

        if (email == null || code == null || newPassword == null ||
                email.isEmpty() || code.isEmpty() || newPassword.isEmpty()) {
            response.put("message", "이메일, 인증 코드 및 새 비밀번호를 모두 입력해주세요.");
            return ResponseEntity.badRequest().body(response);
        }

        if (authService.verifyVerificationCode(email, code)) {
            if (authService.resetPassword(email, newPassword)) {
                response.put("message", "비밀번호가 성공적으로 재설정되었습니다.");
                return ResponseEntity.ok(response);
            } else {
                response.put("message", "비밀번호 재설정 중 오류가 발생했습니다.");
                return ResponseEntity.status(500).body(response);
            }
        } else {
            response.put("message", "인증 코드가 유효하지 않습니다.");
            return ResponseEntity.status(400).body(response);
        }
    }

    // ✅ 사용자 정보 조회
    @GetMapping("/user-info")
    public ResponseEntity<Map<String, Object>> getUserInfo(@RequestParam String email) {
        Optional<User> userOpt = authService.findUserByEmail(email);
        Map<String, Object> response = new HashMap<>();

        if (userOpt.isPresent()) {
            User user = userOpt.get();
            response.put("name", user.getName());
            response.put("phone", user.getPhone());
            response.put("email", user.getEmail());
            return ResponseEntity.ok(response);
        } else {
            response.put("message", "해당 이메일의 사용자를 찾을 수 없습니다.");
            return ResponseEntity.status(404).body(response);
        }
    }

    // ✅ 사용자 정보 수정
    @PutMapping("/user-info")
    public ResponseEntity<Map<String, String>> updateUserInfo(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String name = request.get("name");
        String phone = request.get("phone");

        Map<String, String> response = new HashMap<>();

        if (email == null || name == null || phone == null ||
                email.isEmpty() || name.isEmpty() || phone.isEmpty()) {
            response.put("message", "이메일, 이름, 전화번호를 모두 입력해주세요.");
            return ResponseEntity.badRequest().body(response);
        }

        if (authService.updateUserInfo(email, name, phone)) {
            response.put("message", "사용자 정보가 성공적으로 업데이트되었습니다.");
            return ResponseEntity.ok(response);
        } else {
            response.put("message", "해당 이메일의 사용자를 찾을 수 없습니다.");
            return ResponseEntity.status(404).body(response);
        }
    }
}
