import cv2
import numpy as np
import time

class Visualizer:
    """Hiện thực các phương thức để vẽ bounding box, trạng thái, và thống kê lên frame video."""
    def __init__(self, config):
        self.config = config
        self.colors = {
            'moving': (0, 0, 255),      # Đỏ - di chuyển
            'stopped': (255, 255, 255), # Trắng - dừng
            'violation': (0, 0, 255),   # Đỏ - vi phạm
            'text': (255, 255, 255),    # Trắng
            'stats': (255, 255, 0)      # Vàng cho thống kê
        }
        self.font_small = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale_small = 0.4
        self.font_scale_normal = 0.5
        self.thickness = 1  # Mỏng nhất có thể

    def draw_vehicles_fast(self, frame, vehicles, assigned_detections):
        """Phiên bản tối ưu tốc độ - chỉ vẽ những gì thực sự cần thiết"""
        current_time = time.time()
        for vehicle_id, vehicle in vehicles.items():
            if not self._is_vehicle_visible(vehicle, current_time):
                continue
            box = self._get_vehicle_box(vehicle, assigned_detections, vehicle_id)
            if box is None:
                continue
            x1, y1, x2, y2 = box
            cls = getattr(vehicle, 'vehicle_class', 2)
            # Xác định trạng thái màu sắc
            color, should_draw_box, status_text = self._get_vehicle_visual_info(vehicle, current_time)
            if should_draw_box:
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
            if status_text and should_draw_box:
                vehicle_name = self.config.VEHICLE_NAMES.get(cls, "Xe")
                label = f"ID:{vehicle_id} {status_text}"
                cv2.putText(frame, label, (x1, max(y1-5, 15)),
                           self.font_small, self.font_scale_normal, color, self.thickness)

    def _is_vehicle_visible(self, vehicle, current_time):
        if not hasattr(vehicle, 'last_seen'):
            return True
        if current_time - vehicle.last_seen > 2.0:
            return False
        return True

    def _get_vehicle_box(self, vehicle, assigned_detections, vehicle_id):
        if vehicle_id in assigned_detections:
            _, detection = assigned_detections[vehicle_id]
            return detection['box']
        elif hasattr(vehicle, 'last_box') and vehicle.last_box:
            return vehicle.last_box
        else:
            return None

    def _get_vehicle_visual_info(self, vehicle, current_time):
        effective_status = getattr(vehicle, 'effective_status', 'moving')
        color = self.colors['moving']
        should_draw_box = False
        status_text = ""
        if (effective_status == 'stopped' and hasattr(vehicle, 'status_frames') \
                and vehicle.status_frames >= self.config.MIN_FRAMES_STOP):
            should_draw_box = True
            if hasattr(vehicle, 'stop_start_time') and vehicle.stop_start_time:
                stop_duration = current_time - vehicle.stop_start_time
                if stop_duration >= self.config.MAX_STOP_TIME_BEFORE_CAPTURE:
                    color = self.colors['violation']  # Đỏ khi vi phạm
                    status_text = "VI PHAM!"
                else:
                    color = self.colors['stopped']    # Trắng khi chỉ dừng
                    status_text = f"DUNG:{int(stop_duration)}s"
            else:
                color = self.colors['stopped']
                status_text = "DUNG"
        return color, should_draw_box, status_text

    # Các hàm sau giữ nguyên
    def draw_vehicles_simple(self, frame, vehicles):
        current_time = time.time()
        violation_count = 0
        for vehicle_id, vehicle in vehicles.items():
            if not self._is_vehicle_violating(vehicle, current_time):
                continue
            box = getattr(vehicle, 'current_box', None) or getattr(vehicle, 'last_box', None)
            if box is None:
                continue
            x1, y1, x2, y2 = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), self.colors['violation'], 1)
            label = f"VI PHAM ID:{vehicle_id} | DUNG QUA {int(current_time - vehicle.stop_start_time)}s"
            cv2.putText(frame, label, (x1, max(y1-10, 20)),
                       self.font_small, 0.5, self.colors['violation'], 1)
            violation_count += 1
        return violation_count

    def _is_vehicle_violating(self, vehicle, current_time):
        if not (hasattr(vehicle, 'stop_start_time') and vehicle.stop_start_time):
            return False
        stop_duration = current_time - vehicle.stop_start_time
        return (stop_duration >= self.config.MAX_STOP_TIME_BEFORE_CAPTURE and
                getattr(vehicle, 'status_frames', 0) >= self.config.MIN_FRAMES_STOP)

    def draw_statistics_fast(self, frame, stats):
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (270, 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        y_pos = 25
        line_height = 25
        stats_info = [
            (f"Tong xe: {stats.get('total', 0)}", self.colors['text']),
            (f"Dang dung: {stats.get('stopped', 0)} | Vi pham: {stats.get('violations', 0)}", self.colors['stopped']),
            (f"Thoi gian: {time.strftime('%H:%M:%S')}", self.colors['text'])
        ]
        for text, color in stats_info:
            cv2.putText(frame, text, (10, y_pos), self.font_small, 0.6, color, 1)
            y_pos += line_height
    def draw_vehicles(self, frame, vehicles, assigned_detections):
        return self.draw_vehicles_fast(frame, vehicles, assigned_detections)
    def draw_statistics(self, frame, stats):
        return self.draw_statistics_fast(frame, stats)