package com.example.unifiedbackend.service;

import com.example.unifiedbackend.dto.AuthRequest;
import com.example.unifiedbackend.dto.ChangePasswordRequest;
import com.example.unifiedbackend.entity.User;
import com.example.unifiedbackend.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

@Service
public class AuthService {
    private final UserRepository userRepository;
    private final Map<String, String> verificationCodes = new HashMap<>();

    public AuthService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public boolean signup(AuthRequest request) {
        if (userRepository.findByEmail(request.getEmail()).isPresent()) {
            return false;
        }

        User user = new User();
        user.setEmail(request.getEmail());
        user.setPassword(request.getPassword()); // 실제로는 해싱 필요
        user.setName(request.getName()); // 이름 설정 추가
        user.setPhone(request.getPhone()); // 전화번호 설정 추가
        userRepository.save(user);
        return true;
    }

    public boolean login(AuthRequest request) {
        return userRepository.findByEmail(request.getEmail())
                .map(user -> user.getPassword().equals(request.getPassword()))
                .orElse(false);
    }

    // 비밀번호 변경 로직 추가
    public boolean changePassword(ChangePasswordRequest request) {
        return userRepository.findByEmail(request.getEmail())
                .map(user -> {
                    // 현재 비밀번호 확인 (실제로는 해싱된 비밀번호 비교 필요)
                    if (user.getPassword().equals(request.getCurrentPassword())) {
                        // 새 비밀번호로 업데이트 (실제로는 해싱하여 저장 필요)
                        user.setPassword(request.getNewPassword());
                        userRepository.save(user);
                        return true; // 변경 성공
                    } else {
                        return false; // 현재 비밀번호 불일치
                    }
                })
                .orElse(false); // 사용자 없음
    }

    // 이름으로 이메일 찾는 로직 추가
    public Optional<String> findEmailByName(String name) {
        return userRepository.findByName(name)
                .map(User::getEmail); // 사용자 엔티티에서 이메일 가져오기
    }

    // 이름과 전화번호로 이메일 목록 찾는 로직 추가
    public List<String> findEmailsByNameAndPhone(String name, String phone) {
        return userRepository.findByNameAndPhone(name, phone).stream()
                .map(User::getEmail) // 사용자 엔티티에서 이메일 가져오기
                .collect(Collectors.toList()); // 이메일 목록으로 수집
    }

    // 이메일로 인증 코드 발송 (생성 및 저장) - 실제 발송 기능은 미구현
    public boolean sendVerificationCode(String email) {
        Optional<User> userOptional = userRepository.findByEmail(email);
        if (userOptional.isPresent()) {
            // 4자리 랜덤 코드 생성
            String code = String.format("%04d", new Random().nextInt(10000));
            verificationCodes.put(email, code); // 이메일과 코드 저장
            System.out.println("[" + email + "] 비밀번호 찾기 인증 코드: " + code); // 콘솔에 코드 출력
            return true;
        } else {
            return false; // 해당 이메일 사용자가 없음
        }
    }

    // 인증 코드 확인
    public boolean verifyVerificationCode(String email, String code) {
        // 저장된 코드와 일치하고 코드가 존재하는지 확인 (만료 시간은 고려 안 함)
        return verificationCodes.containsKey(email) && verificationCodes.get(email).equals(code);
    }

    // 비밀번호 재설정
    public boolean resetPassword(String email, String newPassword) {
        Optional<User> userOptional = userRepository.findByEmail(email);
        if (userOptional.isPresent()) {
            User user = userOptional.get();
            user.setPassword(newPassword); // 실제로는 새 비밀번호 해싱 필요
            userRepository.save(user);
            verificationCodes.remove(email); // 코드 사용 후 삭제
            return true;
        } else {
            return false; // 해당 이메일 사용자가 없음
        }
    }

    // 이메일로 저장된 인증 코드 가져오기 (개발/테스트 목적)
    public String getVerificationCode(String email) {
        return verificationCodes.get(email);
    }

    // 이메일로 사용자 찾기
    public Optional<User> findUserByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    // 사용자 정보 업데이트 (이름, 전화번호)
    public boolean updateUserInfo(String email, String name, String phone) {
        Optional<User> userOptional = userRepository.findByEmail(email);
        if (userOptional.isPresent()) {
            User user = userOptional.get();
            user.setName(name);
            user.setPhone(phone);
            userRepository.save(user);
            return true; // 업데이트 성공
        } else {
            return false; // 해당 이메일 사용자가 없음
        }
    }
}
