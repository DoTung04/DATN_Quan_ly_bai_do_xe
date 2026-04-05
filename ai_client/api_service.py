import requests

BACKEND_URL = "http://localhost:8080/api/parking/check"

def check_vehicle(plate_number, vehicle_type):
    """
    Gửi thông tin xe lên Backend
    vehicle_type: 0 (Ô tô) hoặc 1 (Xe máy)
    """
    try:
        payload = {
            "plateNumber": plate_number,
            "vehicleType": vehicle_type
        }
        response = requests.post(BACKEND_URL, json=payload, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "ERROR", "message": f"Server báo lỗi HTTP: {response.status_code}"}
    except Exception as e:
        return {"status": "ERROR", "message": f"Không thể kết nối Backend: {str(e)}"}
