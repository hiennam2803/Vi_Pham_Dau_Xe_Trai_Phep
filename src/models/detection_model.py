from ultralytics import YOLO
import numpy as np

class DetectionModel:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)
        
    def detect_vehicles(self, frame, config):
        """Detect vehicles in frame with filtering"""
        results = self.model(frame, conf=0.6, iou=0.5)
        current_detections = []
        
        for box in results[0].boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Only process cars and motorbikes with class-specific thresholds
            if cls in [2, 3] and conf >= config.VEHICLE_CONFIDENCE_THRESHOLDS.get(cls, config.CONFIDENCE_THRESHOLD):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                
                # Filter by bounding box size
                box_width = x2 - x1
                box_height = y2 - y1
                box_area = box_width * box_height
                
                if (box_area >= config.MIN_BOX_AREA and 
                    box_width >= config.MIN_BOX_WIDTH and 
                    box_height >= config.MIN_BOX_HEIGHT):
                    
                    current_detections.append((cls, {
                        'box': (x1, y1, x2, y2),
                        'center': (cx, cy),
                        'confidence': conf
                    }))
                    
        return current_detections