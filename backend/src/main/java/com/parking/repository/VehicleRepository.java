package com.parking.repository;

import com.parking.model.Vehicle;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface VehicleRepository extends JpaRepository<Vehicle, Long> {
    
    // Tìm xe dựa trên biển số
    Optional<Vehicle> findByPlateNumber(String plateNumber);
}
