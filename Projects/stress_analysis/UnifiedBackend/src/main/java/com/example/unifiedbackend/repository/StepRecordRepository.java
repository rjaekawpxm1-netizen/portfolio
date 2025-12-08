package com.example.unifiedbackend.repository;

import com.example.unifiedbackend.entity.StepRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface StepRecordRepository extends JpaRepository<StepRecord, Long> {
    List<StepRecord> findByEmailOrderByDateDesc(String email);
}
