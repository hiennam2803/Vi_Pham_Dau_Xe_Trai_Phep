import cv2
import os
import datetime
import time
from pathlib import Path

class CaptureManager:
    def __init__(self, config):
        self.config = config
        self.setup_capture_directory()
        
    def setup_capture_directory(self):
        """Tạo thư mục lưu ảnh nếu chưa tồn tại"""
        capture_path = Path(self.config.CAPTURE_DIR)
        # Tạo thư mục cùng các thư mục cha nếu cần (ví dụ 'capture/picture')
        capture_path.mkdir(parents=True, exist_ok=True)
        try:
            abs_path = capture_path.resolve()
        except Exception:
            abs_path = capture_path.absolute()
        print(f"Thư mục lưu ảnh: {abs_path}")
        
    def capture_violation(self, frame, vehicle, detections=None):
        """Chụp ảnh vi phạm"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            vehicle_name = self.config.VEHICLE_NAMES.get(vehicle.vehicle_class, "Unknown")
            # Làm sạch tên xe để dùng trong tên file (thay khoảng trắng và ký tự đặc biệt)
            vehicle_name_clean = vehicle_name.replace(" ", "_")
            # Map Vietnamese names to English for filename safety
            name_map = {"Xe_hoi": "Car", "Xe_may": "Motorbike"}
            vehicle_name_clean = name_map.get(vehicle_name_clean, vehicle_name_clean)
            
            # Kiểm tra last_box hợp lệ
            if not hasattr(vehicle, 'last_box') or vehicle.last_box is None:
                print(f"Lỗi: Vehicle {vehicle.id} không có last_box hợp lệ")
                return False
            
            if self.config.SAVE_FULL_FRAME:
                # Lưu toàn bộ frame với bounding box
                frame_copy = frame.copy()
                
                # Vẽ bounding box đậm cho xe vi phạm
                x1, y1, x2, y2 = map(int, vehicle.last_box)
                # Đảm bảo coordinates hợp lệ
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(frame.shape[1], x2)
                y2 = min(frame.shape[0], y2)
                
                cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 0, 255), 3)
                
                # Thông tin vi phạm
                info_text = f"VI PHAM: {vehicle_name} ID:{vehicle.id}"
                time_text = f"Thoi gian: {datetime.datetime.now().strftime('%H:%M:%S')}"
                stop_duration = int(time.time() - vehicle.stop_start_time) if vehicle.stop_start_time else 0
                duration_text = f"Da dung: {stop_duration}s"
                
                cv2.putText(frame_copy, info_text, (x1, y1 - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame_copy, time_text, (x1, y1 - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.putText(frame_copy, duration_text, (x1, y1 - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                filename = f"{vehicle.id}_{vehicle_name_clean}_{timestamp}.jpg"
                filepath = os.path.join(self.config.CAPTURE_DIR, filename)
                
                if cv2.imwrite(filepath, frame_copy):
                    print(f"Đã chụp ảnh vi phạm: {filename}")
                    vehicle.last_captured_filename = filename
                    vehicle.mark_captured()
                    return True
                else:
                    print(f"Lỗi: Không thể lưu file {filepath}")
                    return False
                
            else:
                # Chỉ lưu crop của xe
                x1, y1, x2, y2 = map(int, vehicle.last_box)
                # Đảm bảo coordinates hợp lệ
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(frame.shape[1], x2)
                y2 = min(frame.shape[0], y2)
                
                if x2 > x1 and y2 > y1:
                    crop_img = frame[y1:y2, x1:x2]
                    
                    if crop_img.size > 0:
                        filename = f"violation_{vehicle.id}_{vehicle_name_clean}_{timestamp}_crop.jpg"
                        filepath = os.path.join(self.config.CAPTURE_DIR, filename)
                        if cv2.imwrite(filepath, crop_img):
                            print(f"Đã chụp ảnh vi phạm: {filename}")
                            vehicle.mark_captured()
                            return True
                        else:
                            print(f"Lỗi: Không thể lưu file {filepath}")
                            return False
                    else:
                        print(f"Lỗi: Crop image trống cho vehicle {vehicle.id}")
                        return False
                else:
                    print(f"Lỗi: Tọa độ bounding box không hợp lệ cho vehicle {vehicle.id}")
                    return False
            
        except Exception as e:
            print(f"Lỗi khi chụp ảnh: {e}")
            import traceback
            traceback.print_exc()
            return False