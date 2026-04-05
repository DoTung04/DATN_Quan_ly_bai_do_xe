package com.parking.dto;

import lombok.Data;

@Data
public class ParkingRequest {
    private String plateNumber;
    private Integer vehicleType; // 0: Ô tô, 1: Xe máy
}
