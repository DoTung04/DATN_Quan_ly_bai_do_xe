import cv2
import easyocr
import re
from collections import Counter
from ultralytics import YOLO
from ai_client.camera import CameraStream

def preprocess_image(image):
    # 1. Chuyển sang ảnh xám
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2. Cân bằng ánh sáng (CLAHE - Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    
    # 3. Phóng to ảnh để EasyOCR lấy được kích thước nét chữ đạt chuẩn
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    
    # 4. Lọc mịn giữ biên (Bilateral Filter khử hạt nhiễu)
    blur = cv2.bilateralFilter(gray, 11, 17, 17)
    
    return blur

def clean_text(text):
    # 1. Loại bỏ các ký tự rác sinh ra do OCR
    raw_str = re.sub(r'[^A-Z0-9]', '', text.upper())
    
    # MẢNG HẬU XỬ LÝ (POST-PROCESSING) DÀNH RIÊNG CHO ĐỊNH DẠNG BIỂN SỐ VN
    # Biển thường có dạng: [2 Số] [1 Chữ] [1 Số/Chữ] - [4 hoặc 5 Số]
    # Ví dụ: 29Z7-4843 (8 ký tự)
    # Ở đây xử lý lỗi kinh điển: Máy lầm chữ Z và số 2, B và 8, S và 5...
    dict_char_to_num = {'O': '0', 'D': '0', 'I': '1', 'Z': '2', 'S': '5', 'B': '8', 'G': '6', 'A': '4'}
    dict_num_to_char = {'0': 'D', '1': 'I', '2': 'Z', '5': 'S', '8': 'B', '4': 'A', '6': 'G'}
    
    if len(raw_str) < 7:
        return raw_str
        
    formatted = list(raw_str)
    
    # Luật 1: Hai ký tự đầu tiên (Mã tỉnh) bắt buộc phải là SỐ
    for i in range(0, min(2, len(formatted))):
        if formatted[i] in dict_char_to_num:
            formatted[i] = dict_char_to_num[formatted[i]]
            
    # Luật 2: Ký tự thứ 3 (Series đăng ký) bắt buộc phải là CHỮ CÁI
    if formatted[2] in dict_num_to_char:
        formatted[2] = dict_num_to_char[formatted[2]]
        
    # Ký tự thứ 4 có thể là Số (xe máy: Z7) hoặc Chữ (xe hơi: LD, KT), tạm thời giữ nguyên
    
    # Luật 3: Từ ký tự thứ 5 trở đi (Số thứ tự xe cuối biển) LUÔN LUÔN LUÔN LÀ SỐ
    # Bắt cứ chữ cái đui mù nào vào đây đều biến thành Số!
    for i in range(4, len(formatted)):
        if formatted[i] in dict_char_to_num:
            formatted[i] = dict_char_to_num[formatted[i]]
            
    return "".join(formatted)

def main():
    print("Bắt đầu tải EasyOCR...")
    reader = easyocr.Reader(['en'], gpu=True) 
    
    print("Đang tải mô hình YOLO...")
    model = YOLO("runs/detect/train_last/weights/best.pt")
    
    print("Khởi động Webcam...")
    cam = CameraStream(src=0)
    
    # --- THUẬT TOÁN CHỐNG NHIỄU VÀ CHỐT KẾT QUẢ ---
    plate_buffer = []      
    locked_plate = None    
    frames_since_locked = 0
    
    print("Đã bật Webcam! Đưa biển số vào và giữ nguyên khoảng 1 giây để hệ thống chốt.")
    
    while True:
        ret, frame = cam.get_frame()
        if not ret:
            break
            
        results = model.predict(source=frame, conf=0.5, verbose=False)
        annotated_frame = results[0].plot()
        
        if locked_plate:
            cv2.putText(annotated_frame, f"DA CHOT: {locked_plate}", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
            
            frames_since_locked += 1
            if frames_since_locked > 60:
                locked_plate = None
                plate_buffer.clear()
                frames_since_locked = 0
                
        else:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                h, w, _ = frame.shape
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                
                cropped_img = frame[y1:y2, x1:x2]
                
                if cropped_img.size != 0:
                    processed_img = preprocess_image(cropped_img)
                    ocr_results = reader.readtext(processed_img)
                    
                    full_text = ""
                    for (bbox, text, prob) in ocr_results:
                        if prob > 0.2: 
                            full_text += text
                    
                    clean_plate = clean_text(full_text)
                    
                    if len(clean_plate) >= 6: 
                        plate_buffer.append(clean_plate)
                        
                        cv2.putText(annotated_frame, f"Dang quet: {clean_plate}", (x1, y1 - 15), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                        
                        if len(plate_buffer) > 15:
                            plate_buffer.pop(0)
                        
                        counter = Counter(plate_buffer)
                        most_common_plate, count = counter.most_common(1)[0]
                        
                        if count >= 3: # Đã giảm xuống 3 lần lặp là ăn luôn cho nhạy
                            locked_plate = most_common_plate
                            print("\n" + "==================================================")
                            print(f"XÁC NHẬN CHÍNH THỨC: Tìm thấy xe mang biển số {locked_plate}")
                            print("SẴN SÀNG KIỂM TRA PHÍ & LƯU DATABASE MYSQL")
                            print("==================================================\n")
                            plate_buffer.clear()
                            break 
        
        cv2.imshow("He thong Quan ly Bai xe Nhanh & Chinh Xac", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Đang thoát chương trình...")
            break
            
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
