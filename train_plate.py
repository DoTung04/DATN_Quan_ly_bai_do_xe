import torch
from ultralytics import YOLO

def main():
    print("Kiem tra CUDA:", torch.cuda.is_available())
    
    # Bắt đầu train từ model nano
    model = YOLO("yolov8n.pt")
    
    print("Bắt đầu huấn luyện mô hình nhận diện Biển Số...")
    # Chú ý: Cần đảm bảo bạn đã chép bộ dữ liệu vào thư mục dataset_plate
    # và file cấu hình nằm ở dataset_plate/data.yaml
    results = model.train(
        data="dataset_plate/data.yaml", 
        epochs=30,      # Bạn có thể đổi thành 50 nếu muốn tăng độ chính xác
        imgsz=640,
        device=0 if torch.cuda.is_available() else 'cpu'
    )
    
    print("==================================================")
    print("Huấn luyện BIỂN SỐ hoàn tất! Model mới được lưu tại:", results.save_dir)
    print("==================================================")

if __name__ == '__main__':
    main()
