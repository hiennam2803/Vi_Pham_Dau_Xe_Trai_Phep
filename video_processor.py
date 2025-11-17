import cv2
import time
from config import Config
from models.detection_model import DetectionModel
from tracker.vehicle_tracker import VehicleTracker
from utils.visualizer import Visualizer
from capture.capture_manager import CaptureManager
from report.report_mail_manager import ReportMailManager
import os

def process_video(source):
    """
    Xử lý video từ nguồn (file hoặc webcam) để nhận diện, phát hiện vi phạm và gửi email báo cáo.
    """
    config = Config()
    detector = DetectionModel()
    tracker = VehicleTracker(config)
    visualizer = Visualizer(config)
    capture_manager = CaptureManager(config)
    mailer = ReportMailManager(
        sender_email="ukikaitovn@gmail.com",
        app_password="yvaectmodvzsxtqo",
        receiver_email="vhdt283@gmail.com"
    )
    
    # Mở video
    if source == '0' or source == 0:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    else:
        cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"Lỗi: Không thể mở nguồn: {source}")
        return False
    
    # Thông tin video
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Video: {width}x{height}, FPS gốc: {original_fps}")
    
    # Biến đo FPS
    frame_count = 0
    start_time = time.time()
    fps = 0
    last_fps_time = start_time
    fps_frame_count = 0
    
    # Tối ưu hóa
    violation_check_interval = max(5, int(original_fps * 3))  # Giảm kiểm tra vi phạm
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            fps_frame_count += 1
            
            # Bỏ qua frame để tăng FPS
            if config.SKIP_FRAMES > 0 and frame_count % (config.SKIP_FRAMES + 1) != 0:
                continue
            
            # Đo FPS mỗi giây
            current_time = time.time()
            if current_time - last_fps_time >= 1.0:
                fps = fps_frame_count / (current_time - last_fps_time)
                last_fps_time = current_time
                fps_frame_count = 0
                print(f"FPS: {fps:.1f}, Frames: {frame_count}")
            
            # Phát hiện phương tiện (đã có skip frame trong detection)
            detections = detector.detect_vehicles(frame, config)
            
            # Cập nhật tracker
            assigned_detections = tracker.update(detections)
            
            # Kiểm tra vi phạm ít thường xuyên hơn
            if frame_count % violation_check_interval == 0:
                violations = tracker.check_violations()
                for vehicle in violations:
                    picture = capture_manager.capture_violation(frame, vehicle, assigned_detections)
                    if picture:
                        print(f"Đã chụp ảnh vi phạm cho xe ID: {vehicle.id}")
                        try:
                            mailer.send_violation_report(
                                os.path.join(config.CAPTURE_DIR, vehicle.last_captured_filename),
                                picture
                            )
                            print("Đã gửi mail báo cáo vi phạm.")
                        except Exception as e:
                            print(f"Lỗi gửi mail: {e}")
            
            # Vẽ kết quả (đơn giản hóa) - sử dụng phương thức đơn giản nhất
            # Lấy thống kê từ tracker
            stats = tracker.get_statistics()
            stats['fps'] = fps  # Thêm FPS vào thống kê
            
            # Vẽ vehicles và thống kê
            visualizer.draw_vehicles_simple(frame, tracker.vehicles)
            visualizer.draw_statistics_fast(frame, stats)
            
            # Hiển thị FPS (đã có trong draw_statistics_fast nên có thể bỏ dòng này nếu muốn)
            # cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
            #            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Hiển thị frame nhỏ hơn nếu cần
            display_frame = frame
            if width > 1280:
                scale = 1280 / width
                new_width = 1280
                new_height = int(height * scale)
                display_frame = cv2.resize(frame, (new_width, new_height))
            
            cv2.imshow('Vehicle Detection', display_frame)
            
            # Thoát nhanh
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
                
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    return True