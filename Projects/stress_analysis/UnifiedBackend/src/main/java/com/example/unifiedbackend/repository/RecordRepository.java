package com.example.unifiedbackend.repository;

import com.example.unifiedbackend.entity.Record;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface RecordRepository extends JpaRepository<Record, Long> {
    List<Record> findByEmail(String email);
    List<Record> findByEmailAndFavoriteTrue(String email);
    List<Record> findByFavoriteTrue();
}
