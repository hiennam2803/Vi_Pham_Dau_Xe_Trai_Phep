import cv2
import argparse
import sys
import os
from config import Config
from models.detection_model import DetectionModel
from tracker.vehicle_tracker import VehicleTracker
from utils.visualizer import Visualizer
from capture.capture_manager import CaptureManager  # THÊM MỚI

def process_video(source):
    """Xử lý video hoặc webcam"""
    # Khởi tạo các component
    config = Config()
    detector = DetectionModel()
    tracker = VehicleTracker(config)
    visualizer = Visualizer(config)
    capture_manager = CaptureManager(config)  # THÊM MỚI
    
    # Mở video hoặc webcam
    if source == '0' or source == 0:
        cap = cv2.VideoCapture(0)
        print("Đang mở webcam...")
    else:
        cap = cv2.VideoCapture(source)
        print(f"Đang mở video: {source}")
    
    if not cap.isOpened():
        print(f"Lỗi: Không thể mở video/webcam từ nguồn: {source}")
        return False
    
    # Lấy thông tin video
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30  # Default FPS nếu không xác định được
        print("Cảnh báo: Không thể xác định FPS, sử dụng giá trị mặc định: 30")
    
    fps = int(fps)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"FPS: {fps}, Kích thước: {width}x{height}")
    
    frame_count = 0
    violation_check_interval = max(1, fps * 2)  # Kiểm tra mỗi 2 giây, tối thiểu 1 frame
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Không thể đọc frame hoặc video đã kết thúc")
                break
            
            frame_count += 1
            
            # Phát hiện phương tiện
            detections = detector.detect_vehicles(frame, config)
            
            # Cập nhật tracker
            assigned_detections = tracker.update(detections)
            
            # KIỂM TRA VI PHẠM VÀ CHỤP ẢNH - Kiểm tra định kỳ
            if violation_check_interval > 0 and frame_count % violation_check_interval == 0:
                violations = tracker.check_violations()
                for vehicle in violations:
                    if capture_manager.capture_violation(frame, vehicle, assigned_detections):
                        print(f"Đã chụp ảnh vi phạm cho xe ID: {vehicle.id}")
            
            # Vẽ kết quả lên frame
            visualizer.draw_vehicles(frame, tracker.vehicles, assigned_detections)
            
            # Vẽ thống kê (thêm thông tin vi phạm)
            stats = tracker.get_statistics()
            visualizer.draw_statistics(frame, stats)
            
            # Hiển thị frame
            cv2.imshow('Vi Pham Dau Xe Trai Phep', frame)
            
            # Nhấn 'q' để thoát
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Người dùng nhấn 'q' để thoát")
                break
            
            # Hiển thị tiến trình
            if frame_count % 30 == 0:
                print(f"Đã xử lý {frame_count} frames. Phương tiện: {stats['total']}")
                
    except KeyboardInterrupt:
        print("\nNgười dùng dừng chương trình (Ctrl+C)")
    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Đã đóng video và giải phóng tài nguyên")
    
    return True