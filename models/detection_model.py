from ultralytics import YOLO
import numpy as np
import cv2

class DetectionModel:
    """Mô hình YOLO dùng để phát hiện phương tiện trên khung hình."""
    def __init__(self, model_path='yolov8s.pt'): # Yolo v8 small đối với video, Yolo v8 nano đối với camera
        self.model = YOLO(model_path)
        self.frame_count = 0
        
    def detect_vehicles(self, frame, config):
        """Detect vehicles với skip frame"""
        self.frame_count += 1
        
        if self.frame_count % config.DETECTION_INTERVAL != 0:
            return []
        
        original_height, original_width = frame.shape[:2]
        if original_width > 1280:  # Chỉ resize nếu frame quá lớn
            scale = 1280 / original_width
            new_width = 1280
            new_height = int(original_height * scale)
            frame_resized = cv2.resize(frame, (new_width, new_height))
        else:
            frame_resized = frame
            scale = 1.0
        
        try:
            results = self.model(frame_resized, 
                               conf=0.5, 
                               iou=0.5, 
                               imgsz=config.MODEL_IMG_SIZE,
                               verbose=False,
                               max_det=15,
                               half=False,
                               augment=False)
            
            current_detections = []
            
            for box in results[0].boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                if cls in [2, 3] and conf >= config.VEHICLE_CONFIDENCE_THRESHOLDS.get(cls, config.CONFIDENCE_THRESHOLD):
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    if scale != 1.0:
                        x1 = int(x1 / scale)
                        y1 = int(y1 / scale) 
                        x2 = int(x2 / scale)
                        y2 = int(y2 / scale)
                    
                    box_width = x2 - x1
                    box_height = y2 - y1
                    box_area = box_width * box_height
                    
                    if (box_area >= config.MIN_BOX_AREA and 
                        box_width >= config.MIN_BOX_WIDTH and 
                        box_height >= config.MIN_BOX_HEIGHT):
                        
                        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                        
                        current_detections.append((cls, {
                            'box': (x1, y1, x2, y2),
                            'center': (cx, cy),
                            'confidence': conf
                        }))
                        
            return current_detections
            
        except Exception as e:
            print(f"Detection error: {e}")
            return []