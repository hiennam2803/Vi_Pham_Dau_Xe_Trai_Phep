from collections import deque
import numpy as np
import time


class Vehicle:
    """
    Đại diện cho 1 phương tiện được phát hiện và theo dõi.
    Lưu trữ vị trí, trạng thái di chuyển, thời gian dừng, vi phạm,...
    """

    def __init__(self, vehicle_id, vehicle_class, detection_box, center, confidence, frame_count):
        # ID và loại phương tiện (car, motorbike…)
        self.id = vehicle_id
        self.vehicle_class = vehicle_class

        # Tracking history
        self.positions = deque([center], maxlen=30)
        self.last_box = detection_box
        self.center = center

        # Trạng thái di chuyển
        self.status = "unknown"
        self.status_frames = 0
        self.speed_history = deque(maxlen=10)
        self.moving_frames = 0

        # Thời điểm cuối được phát hiện
        self.last_update = frame_count
        self.last_seen_frame = frame_count

        # Độ tin cậy
        self.confidence_history = deque([confidence], maxlen=10)
        self.total_detections = 1

        # Che khuất
        self.is_occluded = False
        self.frozen_status = None
        self.frozen_status_frames = 0

        # Thời gian dừng
        self.stop_start_time = None

        # Chụp vi phạm
        self.last_capture_time = 0
        self.violation_count = 0
        self.has_captured_violation = False

    # --------------------------------------------------------------
    # UPDATE VEHICLE INFO
    # --------------------------------------------------------------
    def update(self, detection_box, center, confidence, frame_count):
        """Cập nhật thông tin khi có detection mới."""
        self.positions.append(center)
        self.last_box = detection_box
        self.center = center
        self.last_update = frame_count
        self.last_seen_frame = frame_count
        self.confidence_history.append(confidence)
        self.total_detections += 1

        # Nếu xe từng bị che khuất nhưng giờ đã thấy lại → bỏ trạng thái frozen
        if self.is_occluded:
            self.is_occluded = False
            self.frozen_status = None
            self.frozen_status_frames = 0

    # --------------------------------------------------------------
    # MOVEMENT & STATUS
    # --------------------------------------------------------------
    def calculate_movement(self, config):
        """Tính toán tốc độ, khoảng cách di chuyển và cập nhật trạng thái."""
        # Tính tốc độ tức thời
        if len(self.positions) >= 2:
            p1 = np.array(self.positions[-1])
            p2 = np.array(self.positions[-2])
            self.speed_history.append(np.linalg.norm(p1 - p2))

        # Tính tốc độ trung bình gần nhất
        distances = []
        if len(self.positions) >= 3:
            for i in range(len(self.positions) - 2, len(self.positions)):
                a = np.array(self.positions[i])
                b = np.array(self.positions[i - 1])
                distances.append(np.linalg.norm(a - b))

        avg_recent_speed = np.mean(distances) if distances else 0
        prev_status = self.status

        # Xác định trạng thái di chuyển
        if avg_recent_speed >= config.MOVE_THRESHOLD:
            # Xe di chuyển
            if self.status == "moving":
                self.status_frames += 1
            else:
                if self.status_frames < config.MIN_FRAMES_MOVE:
                    self.status_frames += 1
                else:
                    self.status = "moving"
                    self.status_frames = 1
        else:
            # Xe dừng
            if self.status == "stopped":
                self.status_frames += 1
            else:
                if self.status_frames < config.MIN_FRAMES_STOP:
                    self.status_frames += 1
                else:
                    self.status = "stopped"
                    self.status_frames = 1

        # Xác định thời điểm xe bắt đầu dừng
        effective_status = self.get_effective_status()
        now = time.time()

        if effective_status == "stopped" and self.status_frames >= config.MIN_FRAMES_STOP:
            if self.stop_start_time is None:
                self.stop_start_time = now
        else:
            self.stop_start_time = None

    # --------------------------------------------------------------
    # VIOLATION CHECK
    # --------------------------------------------------------------
    def check_violation(self, config):
        """
        Trả về True nếu xe bị dừng quá lâu và sẵn sàng chụp vi phạm.
        """
        if self.has_captured_violation:
            return False
        if not config.VIOLATION_CAPTURE_ENABLED:
            return False
        if self.stop_start_time is None:
            return False

        now = time.time()
        stop_duration = now - self.stop_start_time

        if (stop_duration >= config.MAX_STOP_TIME_BEFORE_CAPTURE and
            now - self.last_capture_time >= config.CAPTURE_COOLDOWN):
            return True

        return False

    # --------------------------------------------------------------
    # STATUS HANDLING
    # --------------------------------------------------------------
    def get_effective_status(self):
        """Trả về trạng thái đang dùng (có tính đến che khuất)."""
        return self.frozen_status if self.is_occluded and self.frozen_status else self.status

    def mark_captured(self):
        """Đánh dấu rằng đã chụp vi phạm."""
        self.last_capture_time = time.time()
        self.violation_count += 1
        self.has_captured_violation = True

    def freeze_status(self):
        """Đóng băng trạng thái khi xe bị che khuất."""
        self.is_occluded = True
        self.frozen_status = self.status
        self.frozen_status_frames = self.status_frames

    # --------------------------------------------------------------
    # REMOVE CONDITIONS
    # --------------------------------------------------------------
    def should_remove(self, frame_count, config):
        """
        Kiểm tra xem xe có nên xóa khỏi tracker hay không.
        Dựa trên: tuổi track, confidence, che khuất lâu, mất dấu,...
        """
        frames_since_update = frame_count - self.last_update
        avg_conf = np.mean(list(self.confidence_history)) if self.confidence_history else 0

        too_old = frames_since_update > config.MAX_TRACK_AGE
        occluded_too_long = self.is_occluded and (frame_count - self.last_seen_frame) > config.OCCLUSION_THRESHOLD
        missing_too_long = (frame_count - self.last_seen_frame) > int(config.MISSING_SECONDS * 30)
        low_conf = avg_conf < config.MIN_TRACK_CONFIDENCE and self.total_detections > 5
        too_few_detections = self.total_detections < config.MIN_DETECTIONS_TO_KEEP and frames_since_update > 10

        return (
            (too_old and not self.is_occluded) or
            missing_too_long or
            occluded_too_long or
            low_conf or
            too_few_detections
        )
