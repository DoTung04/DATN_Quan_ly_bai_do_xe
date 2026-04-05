import cv2
import easyocr
from ultralytics import YOLO

class VehicleDetector:
    def __init__(self, model_path="yolov8n.pt"):
        # Load mô hình YOLO (Khi bạn train xong, đổi tham số truyền vào thành dường dẫn file best.pt tương ứng)
        self.model = YOLO(model_path)
        # Khởi tạo OCR reader (hỗ trợ tiếng Việt và tiếng Anh)
        self.reader = easyocr.Reader(['vi', 'en'], gpu=False) # Đổi thành True nếu máy có NVIDIA GPU
        
    def detect_and_read(self, frame):
        """
        Nhận diện ô tô/xe máy qua YOLO, xác định vùng ảnh rồi đọc OCR
        Trả về hình ảnh đã vẽ viền ranh giới (bounding box) và danh sách xe tìm thấy.
        """
        results = self.model(frame, verbose=False)
        annotated_frame = frame.copy()
        
        detected_vehicles = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                
                # Class 0: Car, Class 1: Motorcycle (độ tin cậy > 0.5)
                if cls_id in [0, 1] and conf > 0.5:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Vẽ bounding box
                    color = (0, 255, 0) if cls_id == 0 else (255, 0, 0)
                    label = "Car" if cls_id == 0 else "Motorcycle"
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(annotated_frame, f"{label} {conf:.2f}", (x1, max(0, y1 - 10)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    
                    # Cắt khung chứa phương tiện
                    crop_img = frame[y1:y2, x1:x2]
                    
                    # Trích xuất văn bản từ khung đó TODO: 
                    # Nếu có mô hình Crop biển số riêng biệt (LP) thì kết quả sẽ chính xác hơn, 
                    # ở đây ta OCR trực tiếp trên phần hình ảnh của xe
                    plate_text = self.extract_license_plate(crop_img)
                    if plate_text:
                        detected_vehicles.append({
                            'plate': plate_text,
                            'type': cls_id
                        })
                        
        return annotated_frame, detected_vehicles
        
    def extract_license_plate(self, vehicle_img):
        """
        Đọc text trên khu vực ảnh chứa phương tiện
        """
        if vehicle_img.size == 0:
            return None
            
        ocr_result = self.reader.readtext(vehicle_img)
        text = ""
        for (bbox, text_part, prob) in ocr_result:
            if prob > 0.3: # Lọc những dự đoán thấp
                # Loại bỏ ký tự đặc biệt, dấu cách
                cleaned = ''.join(e for e in text_part if e.isalnum())
                text += cleaned
                
        # Giả định biển số xe Việt Nam thường dài ít nhất 4 ký tự (chữ + số)
        return text if len(text) >= 4 else None
