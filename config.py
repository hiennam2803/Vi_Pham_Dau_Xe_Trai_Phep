# Configuration constants
class Config:
    # Movement detection thresholds
    MOVE_THRESHOLD = 1
    STOP_THRESHOLD = 1.5
    MIN_FRAMES_STOP = 15
    MIN_FRAMES_MOVE = 5
    CONFIDENCE_THRESHOLD = 0.3
    
    # Vehicle-specific confidence thresholds
    VEHICLE_CONFIDENCE_THRESHOLDS = {
        2: 0.5,  # car
        3: 0.35, # motorbike
    }
    
    # Bounding box filters
    MIN_BOX_AREA = 500
    MIN_BOX_WIDTH = 20
    MIN_BOX_HEIGHT = 20
    
    # Tracking parameters
    IOU_THRESHOLD = 0.4
    MAX_TRACK_AGE = 60
    MIN_TRACK_CONFIDENCE = 0.4
    MIN_DETECTIONS_TO_KEEP = 3
    OCCLUSION_THRESHOLD = 45
    MISSING_SECONDS = 60
    
    # VIOLATION CAPTURE SETTINGS - THÊM MỚI
    VIOLATION_CAPTURE_ENABLED = True
    MAX_STOP_TIME_BEFORE_CAPTURE = 10  # giây
    CAPTURE_DIR = "capture"
    SAVE_FULL_FRAME = True  # Lưu toàn bộ frame hoặc chỉ crop xe
    CAPTURE_COOLDOWN = 30  # giây - thời gian chờ trước khi chụp lại cùng 1 xe
    
    # Vehicle names
    VEHICLE_NAMES = {
        2: "Xe hoi",
        3: "Xe may"
    }
    