from ultralytics import YOLO
import numpy as np
import cv2

class DetectionModel:
    """
    Mô hình YOLO dùng để phát hiện phương tiện (car, motorcycle…).
    Hỗ trợ skip-frame để tăng FPS và auto-resize khi frame quá lớn.
    """

    def __init__(self, model_path='yolov8s.pt'):
        """
        model_path:
            - yolov8s.pt: phù hợp xử lý video.
            - yolov8n.pt: phù hợp camera real-time.
        """
        self.model = YOLO(model_path)
        self.frame_count = 0

    def detect_vehicles(self, frame, config):
        """
        Phát hiện phương tiện với:
            - Skip frame theo config.DETECTION_INTERVAL
            - Resize nếu frame quá lớn (>1280px)
            - Lọc theo class, confidence, kích thước box
        Trả về:
            [(class_id, {box, center, confidence}), ...]
        """
        self.frame_count += 1

        # Bỏ qua detection nếu chưa đến chu kỳ
        if self.frame_count % config.DETECTION_INTERVAL != 0:
            return []

        # Resize nếu khung hình quá lớn để giảm tải GPU/CPU
        original_h, original_w = frame.shape[:2]
        if original_w > 1280:
            scale = 1280 / original_w
            new_size = (1280, int(original_h * scale))
            frame_resized = cv2.resize(frame, new_size)
        else:
            frame_resized = frame
            scale = 1.0

        try:
            # Chạy YOLO
            results = self.model(
                frame_resized,
                conf=0.5,
                iou=0.5,
                imgsz=config.MODEL_IMG_SIZE,
                verbose=False,
                max_det=15,
                half=False,
                augment=False
            )

            detections = []
            boxes = results[0].boxes

            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                # Lọc theo class và confidence
                if cls not in [2, 3]:  # 2=car, 3=motorbike
                    continue

                threshold = config.VEHICLE_CONFIDENCE_THRESHOLDS.get(
                    cls, config.CONFIDENCE_THRESHOLD
                )
                if conf < threshold:
                    continue

                # Lấy bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Convert về kích thước gốc nếu đã resize
                if scale != 1.0:
                    x1 = int(x1 / scale)
                    y1 = int(y1 / scale)
                    x2 = int(x2 / scale)
                    y2 = int(y2 / scale)

                w, h = x2 - x1, y2 - y1
                area = w * h

                # Lọc theo kích thước
                if (area < config.MIN_BOX_AREA or
                    w < config.MIN_BOX_WIDTH or
                    h < config.MIN_BOX_HEIGHT):
                    continue

                # Tính tâm box
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                detections.append((
                    cls,
                    {
                        "box": (x1, y1, x2, y2),
                        "center": (cx, cy),
                        "confidence": conf
                    }
                ))

            return detections

        except Exception as e:
            print(f"[Detection Error] {e}")
            return []
