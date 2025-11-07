import cv2
import argparse
import sys
from config import Config
from models.detection_model import DetectionModel
from tracker.vehicle_tracker import VehicleTracker
from utils.visualizer import Visualizer

def process_video(source):
    """Xử lý video hoặc webcam"""
    # Khởi tạo các component
    config = Config()
    detector = DetectionModel()
    tracker = VehicleTracker(config)
    visualizer = Visualizer(config)
    
    # Mở video hoặc webcam
    if source == '0' or source == 0:
        cap = cv2.VideoCapture(0)
        print("Đang mở webcam...")
    else:
        cap = cv2.VideoCapture(source)
        print(f"Đang mở video: {source}")
    
    # Kiểm tra xem có mở được không
    if not cap.isOpened():
        print(f"Lỗi: Không thể mở video/webcam từ nguồn: {source}")
        return False
    
    # Lấy thông tin video
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"FPS: {fps}, Kích thước: {width}x{height}")
    
    frame_count = 0
    
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
            
            # Vẽ kết quả lên frame
            visualizer.draw_vehicles(frame, tracker.vehicles, assigned_detections)
            
            # Vẽ thống kê
            stats = tracker.get_statistics()
            visualizer.draw_statistics(frame, stats)
            
            # Hiển thị frame
            cv2.imshow('Vi Pham Dau Xe Trai Phep', frame)
            
            # Nhấn 'q' để thoát
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Người dùng nhấn 'q' để thoát")
                break
            
            # Hiển thị tiến trình mỗi 30 frames
            if frame_count % 30 == 0:
                print(f"Đã xử lý {frame_count} frames. Phương tiện hiện tại: {stats['total']}")
                
    except KeyboardInterrupt:
        print("\nNgười dùng dừng chương trình (Ctrl+C)")
    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Giải phóng tài nguyên
        cap.release()
        cv2.destroyAllWindows()
        print("Đã đóng video và giải phóng tài nguyên")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Xử lý video để phát hiện vi phạm đậu xe trái phép')
    parser.add_argument('--source', type=str, default='0', 
                       help='Nguồn video (0 cho webcam hoặc đường dẫn file video)')
    
    args = parser.parse_args()
    
    success = process_video(args.source)
    sys.exit(0 if success else 1)
