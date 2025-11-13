import cv2
import numpy as np
import time

class Visualizer:
    def __init__(self, config):
        self.config = config
        
    def draw_vehicles(self, frame, vehicles, assigned_detections):
        """Draw vehicles and information on frame"""
        for vehicle_id, vehicle in vehicles.items():
            # Lấy thông tin hiển thị
            if vehicle_id in assigned_detections:
                cls, detection = assigned_detections[vehicle_id]
                x1, y1, x2, y2 = detection['box']
                cx, cy = detection['center']
            else:
                if vehicle.is_occluded:
                    x1, y1, x2, y2 = vehicle.last_box
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    cls = vehicle.vehicle_class
                else:
                    continue
                    
            # Xác định trạng thái
            vehicle_name = self.config.VEHICLE_NAMES.get(cls, "Xe khac")
            effective_status = vehicle.get_effective_status()
            
            # -----------------------------
            # CHỌN MÀU + TRẠNG THÁI
            # -----------------------------
            if effective_status == 'stopped' and vehicle.status_frames >= self.config.MIN_FRAMES_STOP:
                if vehicle.stop_start_time is not None:
                    stop_duration = time.time() - vehicle.stop_start_time
                    if stop_duration >= self.config.MAX_STOP_TIME_BEFORE_CAPTURE:
                        color = (0, 0, 255)  # Dỏ - vi phạm
                        status_text = "VI PHAM !!!"
                    else:
                        color = (0, 255, 0)  # Xanh - đang dừng
                        status_text = "DA DUNG"
                else:
                    color = (0, 255, 0)
                    status_text = "DA DUNG"
                    
                if vehicle.is_occluded:
                    status_text += " (CHE KHUAT)"
                    
                #CHỈ XE DỪNG MỚI VẼ KHUNG
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            else:
                # Xe đang di chuyển — chỉ vẽ text, không có khung
                color = (0, 0, 255)
                status_text = ""
                if vehicle.is_occluded and effective_status == 'moving':
                    status_text += ""
            
            
            avg_confidence = np.mean(list(vehicle.confidence_history)) if vehicle.confidence_history else 0
            if (status_text == ""):
                label = f""
                cv2.putText(frame, label, (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(frame, status_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            else:
                label = f"ID:{vehicle_id} {vehicle_name} {status_text} {avg_confidence:.2f}"
                cv2.putText(frame, label, (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(frame, status_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            # Thời gian dừng (nếu có)
            if vehicle.stop_start_time is not None:
                stop_duration = time.time() - vehicle.stop_start_time
                duration_text = f"Dung: {int(stop_duration)}s"
                cv2.putText(frame, duration_text, (x1, y2 + 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Vẽ đường di chuyển (trail)
            if len(vehicle.positions) > 1:
                points = np.array(vehicle.positions, dtype=np.int32)
                cv2.polylines(frame, [points], False, color, 2)

    def draw_statistics(self, frame, stats):
        """Draw statistics on frame"""
        violations_count = int(stats.get('violations', 0))
        cv2.putText(frame, f"Vi pham: {violations_count}", (10, 210), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        y_pos = 30
        stats_color = (255, 255, 255)
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        info_list = [
            (f"Tong so xe: {stats['total']}", stats_color),
            (f"Dang dung: {stats['stopped']}", stats_color),
            (f"Vi pham: {stats.get('violations', 0)}", (0, 255, 255))
        ]
        
        for text, color in info_list:
            cv2.putText(frame, text, (10, y_pos), font, 0.6, color, 2)
            y_pos += 30
