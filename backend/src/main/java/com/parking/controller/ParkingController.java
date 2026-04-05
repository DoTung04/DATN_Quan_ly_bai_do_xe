package com.parking.controller;

import com.parking.dto.ParkingRequest;
import com.parking.service.ParkingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/parking")
public class ParkingController {

    @Autowired
    private ParkingService parkingService;

    @PostMapping("/check")
    public ResponseEntity<Map<String, Object>> checkParking(@RequestBody ParkingRequest request) {
        
        if (request.getPlateNumber() == null || request.getPlateNumber().trim().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("status", "ERROR", "message", "Biển số không hợp lệ"));
        }

        Map<String, Object> result = parkingService.checkVehicle(request.getPlateNumber(), request.getVehicleType());
        return ResponseEntity.ok(result);
    }
}
