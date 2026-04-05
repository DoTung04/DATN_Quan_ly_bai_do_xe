import cv2

class CameraStream:
    def __init__(self, src=0):
        # Hệ điều hành Windows: Dùng cv2.CAP_DSHOW để thiết lập các thông số sâu cấp phần cứng (cướp quyền Auto-Exposure)
        self.src = src
        self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)
        
        # 1. TẮT TÍNH NĂNG TỰ ĐỘNG PHƠI SÁNG (Auto-Exposure)
        # Bị hiện tượng nháy sáng lúc lóa lúc tối ngòm khi giơ biển số (vùng màu trắng tảng to)
        # Các Webcam Windows phổ thông nhận giá trị 0.25 (hoặc 0) cho Manual Exposure.
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25) 
        
        # 2. KHÓA MỨC ĐỘ SÁNG CỐ ĐỊNH (Giá trị này tùy Webcam. Càng âm sâu càng tối)
        # Lốc nãy để -5 bị tối ngòm, tôi vừa nâng lên -4 (khoảng ánh sáng trong phòng)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -4)
        
        # 3. LUÔN LUÔN LẤY NÉT TOÀN DIỆN (TẮT AUTO-FOCUS tránh giật hình lấy nét)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        
    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return False, None
        return True, frame
        
    def release(self):
        self.cap.release()
