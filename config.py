class Config:
    """Các thông số cấu hình hệ thống CarCheck: ngưỡng nhận diện, tracking, lưu ảnh, hành vi xe..."""
    
    # ==========================
    #  CẤU HÌNH HIỂN THỊ
    # ==========================
    VISUALIZER_MODE = 'fast'      # Cách vẽ khung: 'fast' = nhanh nhất, 'simple' = vừa, 'full' = đầy đủ
    DRAW_VEHICLE_TRAILS = False   # Có vẽ đường di chuyển của xe không
    DRAW_CONFIDENCE = False       # Có vẽ % độ tin cậy YOLO trên khung không
    MIN_DISPLAY_CONFIDENCE = 0.3  # Chỉ hiện box nếu confidence >= 0.3

    # ==========================
    #  CẤU HÌNH PHÂN LOẠI HÀNH VI
    # ==========================
    MOVE_THRESHOLD = 1.2          # Nếu xe di chuyển > threshold này → tính là moving
    STOP_THRESHOLD = 2.0          # Nếu xe di chuyển < threshold này → tính là stopped
    MIN_FRAMES_STOP = 8           # Số frame tối thiểu để coi là "đã dừng"
    MIN_FRAMES_MOVE = 3           # Số frame tối thiểu để coi là "đang di chuyển"

    # ==========================
    #  CẤU HÌNH YOLO + LỌC DETECTION
    # ==========================
    CONFIDENCE_THRESHOLD = 0.4    # Ngưỡng YOLO để chấp nhận detection
    VEHICLE_CONFIDENCE_THRESHOLDS = {2: 0.6, 3: 0.45}  

    MIN_BOX_AREA = 200            # Box nhỏ hơn → loại (tránh lỗi phát hiện)
    MIN_BOX_WIDTH = 10            
    MIN_BOX_HEIGHT = 10           

    # ==========================
    #  CẤU HÌNH TRACKING
    # ==========================
    IOU_THRESHOLD = 0.5           # Nếu IoU > x → coi là cùng 1 xe
    MAX_TRACK_AGE = 30            # Xe mất dấu > x frame → xoá track
    MIN_TRACK_CONFIDENCE = 0.5    # Xe có độ tin cậy trung bình < x → xoá track
    MIN_DETECTIONS_TO_KEEP = 2    # Phải detect >= x lần mới giữ xe
    OCCLUSION_THRESHOLD = 50      # Ngưỡng để đánh dấu xe bị che khuất
    MISSING_SECONDS = 30          # Nếu mất > x giây → xoá xe

    # ==========================
    #  CẤU HÌNH FPS – TỐI ƯU HIỆU NĂNG
    # ==========================
    DETECTION_INTERVAL = 2        # Phát hiện mỗi n frame (để tăng FPS)
    MODEL_IMG_SIZE = 320
    SKIP_FRAMES = 1

    # ==========================
    #  CẤU HÌNH CHỤP VI PHẠM
    # ==========================
    VIOLATION_CAPTURE_ENABLED = True   # Bật/tắt tính năng chụp xe vi phạm
    MAX_STOP_TIME_BEFORE_CAPTURE = 3   # Xe dừng >= x giây → tính là vi phạm
    CAPTURE_DIR = 'capture/picture'    # Thư mục lưu ảnh vi phạm
    SAVE_FULL_FRAME = False            # False = chỉ lưu vùng xe vi phạm, không lưu cả frame
    CAPTURE_COOLDOWN = 3600            # Mỗi xe chỉ chụp 1 lần mỗi 60 giây

    # ==========================
    #  CẤU HÌNH TÊN PHƯƠNG TIỆN
    # ==========================
    VEHICLE_NAMES = {
        2: 'Xe hoi',
        3: 'Xe may'
    }
