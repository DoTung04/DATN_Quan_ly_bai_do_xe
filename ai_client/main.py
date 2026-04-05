import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QTextEdit
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from camera import CameraStream
from detector import VehicleDetector

# Import api_service (Đảm bảo đã chạy Backend server ở cổng 8080)
from api_service import check_vehicle

class ParkingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hệ thống Quản lý Bãi đỗ xe - AI Camera")
        self.setGeometry(100, 100, 1024, 600)
        
        # Setup Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        
        # Khung Camera
        self.cam_layout = QVBoxLayout()
        self.video_label = QLabel("Đang mở Camera...")
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("background-color: #222; color: white; text-align: center;")
        self.cam_layout.addWidget(self.video_label)
        self.layout.addLayout(self.cam_layout)
        
        # Khung Thông tin (Text Log)
        self.info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("font-size: 16px; background-color: #f4f4f4; padding: 10px;")
        self.info_layout.addWidget(self.info_text)
        self.layout.addLayout(self.info_layout)
        
        # Init Camera và AI Detector
        self.camera = CameraStream(0) # Camera mặc định
        
        # Lưu ý: Khi train model xong, ta nên đổi 'yolov8n.pt' thành đường dẫn file weights vừa train
        # VD: self.detector = VehicleDetector("../runs/detect/train/weights/best.pt")
        self.detector = VehicleDetector("yolov8n.pt") 
        
        self.is_processing = False
        self.last_plate = "" # Lưu biển số gần nhất để tránh spam API liên tục
        
        # Timer update Frame 30 FPS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)

    def append_log(self, text):
        self.info_text.append(text)
        self.info_text.verticalScrollBar().setValue(self.info_text.verticalScrollBar().maximum())

    def update_frame(self):
        ret, frame = self.camera.get_frame()
        if ret:
            # Nhận diện ảnh qua YOLO + OCR
            annotated_frame, vehicles = self.detector.detect_and_read(frame)
            
            # Xử lý Logic gửi API
            for v in vehicles:
                plate = v['plate']
                v_type = v['type']
                type_name = "Ô tô" if v_type == 0 else "Xe máy"
                
                # Check nếu là xe mới hoặc khác xe gần nhất
                if plate and plate != self.last_plate:
                    self.last_plate = plate
                    self.append_log(f"Đã phát hiện xe: <b>{plate}</b> ({type_name})")
                    
                    # Gọi API kiểm tra (Đồng bộ)
                    # NOTE: Trong thực tế nên dùng QThread để gọi API tránh đơ màn hình khi mạng lag
                    api_result = check_vehicle(plate, v_type)
                    
                    if api_result.get("status") == "ERROR":
                        self.append_log(f"<font color='red'>{api_result.get('message')}</font>")
                    else:
                        msg = api_result.get("message", "N/A")
                        status = api_result.get("status", "")
                        
                        if status == "NEW":
                           self.append_log(f"<font color='blue'><b>XE CHƯA ĐĂNG KÝ:</b> {msg}</font>")
                        elif status == "EXIST":
                           self.append_log(f"<font color='green'><b>ĐÃ THANH TOÁN:</b> {msg}</font>")
                        else:
                           self.append_log(f"Phản hồi từ Server: {msg}")
                    
                    self.append_log("-" * 30)

            # Convert Frame -> PyQt Image Format để hiển thị
            rgb_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_format).scaled(640, 480)
            self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        """Hủy camera khi đóng cửa sổ"""
        self.camera.release()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ParkingApp()
    window.show()
    sys.exit(app.exec_())
