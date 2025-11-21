import cv2
import time
import os

from config import Config
from models.detection_model import DetectionModel
from tracker.vehicle_tracker import VehicleTracker
from utils.visualizer import Visualizer
from capture.capture_manager import CaptureManager
from report.report_mail_manager import ReportMailManager


def process_video(source):
    """
    Xử lý video từ webcam hoặc file:
        - Phát hiện phương tiện
        - Tracking
        - Kiểm tra vi phạm
        - Chụp ảnh vi phạm
        - Gửi email báo cáo
        - Hiển thị video và thống kê
    """
    # Khởi tạo cấu hình và các module
    config = Config()
    detector = DetectionModel()
    tracker = VehicleTracker(config)
    visualizer = Visualizer(config)
    capture_manager = CaptureManager(config)

    # Cấu hình gửi email
    mailer = ReportMailManager(
        sender_email="ukikaitovn@gmail.com",
        app_password="yvaectmodvzsxtqo",
        receiver_email="vhdt283@gmail.com"
    )

    # Mở nguồn video
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

    # Lấy thông số video gốc
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Video: {width}x{height}, FPS gốc: {original_fps}")

    # FPS counters
    frame_count = 0
    fps_frame_count = 0
    last_fps_time = time.time()
    fps = 0

    # Giảm tần suất kiểm tra vi phạm để tiết kiệm CPU
    violation_check_interval = max(5, int(original_fps * 3))

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            fps_frame_count += 1

            # Skip frame để tăng FPS
            if config.SKIP_FRAMES > 0 and frame_count % (config.SKIP_FRAMES + 1) != 0:
                continue

            # Tính FPS mỗi giây
            current_time = time.time()
            if current_time - last_fps_time >= 1.0:
                fps = fps_frame_count / (current_time - last_fps_time)
                last_fps_time = current_time
                fps_frame_count = 0
                print(f"FPS: {fps:.1f}, Frames: {frame_count}")

            # Phát hiện phương tiện
            detections = detector.detect_vehicles(frame, config)

            # Cập nhật tracker
            assigned_detections = tracker.update(detections)

            # Kiểm tra vi phạm theo chu kỳ
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

            # Lấy số liệu thống kê
            stats = tracker.get_statistics()
            stats["fps"] = fps

            # Vẽ bounding box và thống kê
            visualizer.draw_vehicles_simple(frame, tracker.vehicles)
            visualizer.draw_statistics_fast(frame, stats)

            # Thu nhỏ nếu video quá lớn
            display_frame = frame
            if width > 1280:
                scale = 1280 / width
                new_size = (1280, int(height * scale))
                display_frame = cv2.resize(frame, new_size)

            cv2.imshow("Vehicle Detection", display_frame)

            # Thoát khi nhấn 'q'
            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                break

    except Exception as e:
        print(f"Lỗi: {e}")

    finally:
        cap.release()
        cv2.destroyAllWindows()

    return True
