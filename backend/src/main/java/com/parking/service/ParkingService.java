package com.parking.service;

import com.parking.model.Vehicle;
import com.parking.repository.VehicleRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@Service
public class ParkingService {

    @Autowired
    private VehicleRepository vehicleRepository;

    public Map<String, Object> checkVehicle(String plateNumber, Integer vehicleType) {
        Map<String, Object> response = new HashMap<>();

        Optional<Vehicle> existingVehicle = vehicleRepository.findByPlateNumber(plateNumber);

        if (existingVehicle.isPresent()) {
            // Xe đã có trong DB
            response.put("status", "EXIST");
            response.put("message", "Xe đã trả phí rồi");
        } else {
            // Xe chưa có trong DB -> Tạo mới và lưu lại luôn (Giả định thu tiền xong là lưu)
            Vehicle newVehicle = new Vehicle();
            newVehicle.setPlateNumber(plateNumber);
            newVehicle.setVehicleType(vehicleType);
            newVehicle.setEntryTime(LocalDateTime.now());
            newVehicle.setIsPaid(true); // Đánh dấu đã trả phí

            vehicleRepository.save(newVehicle);

            // Tính phí
            int fee = (vehicleType != null && vehicleType == 0) ? 10000 : 5000;
            String typeName = (vehicleType != null && vehicleType == 0) ? "Ô tô" : "Xe máy";

            response.put("status", "NEW");
            response.put("fee", fee);
            response.put("message", "Phí gửi xe " + typeName + " là " + fee + " VND. (Đã tự động lưu vào hệ thống)");
        }

        return response;
    }
}
