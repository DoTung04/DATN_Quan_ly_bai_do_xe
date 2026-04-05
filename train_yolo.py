from ultralytics import YOLO

def main():
    # Khởi tạo mô hình pre-trained YOLOv8 (nano) để tối ưu tốc độ nhận diện realtime
    # Bạn có thể thay đổi "yolov8n.pt" thành "yolov8s.pt" hoặc "yolov8m.pt" để tăng độ chính xác 
    # nhưng sẽ yêu cầu phần cứng mạnh hơn (GPU/CPU xử lý lâu hơn)
    model = YOLO("yolov8n.pt")
    
    # Bắt đầu quá trình huấn luyện
    # Tham số:
    # data: Đường dẫn tới file cấu hình dataset (chứa thông tin class và đường dẫn train/val)
    # epochs: Số lần duyệt qua toàn bộ dataset (có thể điều chỉnh, ví dụ 50, 100)
    # imgsz: Kích thước ảnh đầu vào (thường là 640 với YOLOv8)
    # batch: Số lượng ảnh mỗi lần đưa vào model (tùy dung lượng RAM/VRAM máy bạn, để mặc định autodetect hoặc set 8, 16)
    results = model.train(data="data.yaml", epochs=50, imgsz=640)
    
    print("Huấn luyện hoàn tất! Model lưu tại:", results.save_dir)

if __name__ == '__main__':
    main()

# from ultralytics import YOLO

# def main():
#     model = YOLO("runs/detect/train3/weights/last.pt")

#     results = model.train(
#         data="data.yaml",
#         epochs=50,
#         imgsz=640,
#         device=0,
#         resume=True
#     )

#     print("Huấn luyện hoàn tất! Model lưu tại:", results.save_dir)

# if __name__ == '__main__':
#     main()

import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
