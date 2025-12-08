package com.example.unifiedbackend.repository;

import com.example.unifiedbackend.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
import java.util.List;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    Optional<User> findByName(String name);
    List<User> findByNameAndPhone(String name, String phone);
}
