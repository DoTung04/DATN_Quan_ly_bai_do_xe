package com.parking.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "vehicles")
@Data
@NoArgsConstructor
public class Vehicle {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Biển số xe sẽ là unique để tra cứu
    @Column(name = "plate_number", unique = true, nullable = false)
    private String plateNumber;

    // Phân loại: 0 là Oto, 1 là Xe máy
    @Column(name = "vehicle_type", nullable = false)
    private Integer vehicleType;

    // Thời gian xe gửi vào bãi
    @Column(name = "entry_time")
    private LocalDateTime entryTime;

    // Trạng thái đã trả phí hay chưa. Mặc định là true luôn khi được tạo (Vì hệ thống giả thiết phát hiện xe mới là đã trả tiền)
    @Column(name = "is_paid")
    private Boolean isPaid;
}
