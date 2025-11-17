import numpy as np
import time
from collections import defaultdict
from models.vehicle import Vehicle
import shortuuid

class VehicleTracker:
    """Quản lý và theo dõi các phương tiện di chuyển phát hiện trong khung hình."""

    def __init__(self, config):
        self.config = config
        self.vehicles = {}        # Lưu danh sách vehicle đang theo dõi {id: Vehicle}
        self.next_id = 1          # ID tăng dần (không dùng nữa, vì dùng UUID)
        self.frame_count = 0      # Đếm số frame đã xử lý
        
    def calculate_iou(self, box1, box2):
        """Tính IoU giữa hai bounding box để xem mức độ trùng nhau."""

        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Tính vùng giao nhau
        x1_inter = max(x1_1, x1_2)
        y1_inter = max(y1_1, y1_2)
        x2_inter = min(x2_1, x2_2)
        y2_inter = min(y2_1, y2_2)
        
        if x2_inter <= x1_inter or y2_inter <= y1_inter:
            return 0  # Không giao nhau
        
        inter_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)
        box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0
        
    def assign_vehicle_ids(self, current_detections):
        """
        Gán ID cho các phương tiện bằng cách:
        - So sánh IoU với những xe cũ đã theo dõi
        - Xe nào khớp IoU cao → giữ ID cũ
        - Xe mới → tạo UUID mới
        """

        # Nếu chưa có vehicle nào → gán ID mới hết
        if not self.vehicles:
            assigned_detections = {}
            for cls, det in current_detections:
                random_id = shortuuid.uuid()
                assigned_detections[random_id] = (cls, det)
            return assigned_detections
            
        # Tạo ma trận IoU giữa detection mới và vehicle đang theo dõi
        iou_matrix = np.zeros((len(current_detections), len(self.vehicles)))
        
        for i, (_, det) in enumerate(current_detections):
            for j, (vehicle_id, vehicle) in enumerate(self.vehicles.items()):
                iou_matrix[i, j] = self.calculate_iou(det['box'], vehicle.last_box)
                
        assigned_detections = {}
        used_tracks = set()
        used_detections = set()
        
        # Match detection ↔ vehicle bằng greedy matching
        while True:
            max_iou = 0
            best_i, best_j = -1, -1
            
            # Tìm IoU lớn nhất chưa gán
            for i in range(len(current_detections)):
                if i in used_detections:
                    continue
                for j in range(len(self.vehicles)):
                    if j in used_tracks:
                        continue
                    if iou_matrix[i, j] > max_iou:
                        max_iou = iou_matrix[i, j]
                        best_i, best_j = i, j
                        
            # Nếu IoU nhỏ hơn threshold → dừng
            if max_iou < self.config.IOU_THRESHOLD:
                break
                
            # Gán ID cũ
            track_id = list(self.vehicles.keys())[best_j]
            assigned_detections[track_id] = current_detections[best_i]
            used_tracks.add(best_j)
            used_detections.add(best_i)
            
        # Các detection không match → tạo ID mới
        for i, (cls, det) in enumerate(current_detections):
            if i not in used_detections:
                random_id = shortuuid.uuid()
                assigned_detections[random_id] = (cls, det)
                
        return assigned_detections
        
    def update(self, current_detections):
        """
        Cập nhật tracker theo detection mới:
        - Gán ID
        - Tạo vehicle mới
        - Update vehicle cũ
        - Xử lý occlusion
        - Cleanup vehicle
        """

        self.frame_count += 1
        
        # Gán ID
        assigned_detections = self.assign_vehicle_ids(current_detections)
        
        # Update từng vehicle
        for vehicle_id, (cls, detection) in assigned_detections.items():
            # Xe mới
            if vehicle_id not in self.vehicles:
                self.vehicles[vehicle_id] = Vehicle(
                    vehicle_id, cls, detection['box'], 
                    detection['center'], detection['confidence'], 
                    self.frame_count
                )
            else:
                # Xe đang tồn tại → cập nhật vị trí, tốc độ
                vehicle = self.vehicles[vehicle_id]
                vehicle.update(
                    detection['box'], detection['center'], 
                    detection['confidence'], self.frame_count
                )
                vehicle.calculate_movement(self.config)
                
        # Xử lý mất dấu
        self._handle_occlusion()
        
        # Xoá xe lâu không xuất hiện
        self._cleanup_vehicles()
        
        return assigned_detections
        
    def _handle_occlusion(self):
        """Nếu xe bị che khuất vài frame → freeze trạng thái."""

        for vehicle in self.vehicles.values():
            frames_since_last_seen = self.frame_count - vehicle.last_seen_frame
            
            # Nếu mất dấu > 3 frame → chuyển sang trạng thái bị che khuất
            if frames_since_last_seen > 3 and not vehicle.is_occluded:
                vehicle.freeze_status()
                
            # Nếu đang bị che → tăng bộ đếm
            if vehicle.is_occluded:
                vehicle.frozen_status_frames += 1
    
    def _cleanup_vehicles(self):
        """Xoá các xe quá lâu không xuất hiện hoặc độ tin cậy thấp."""

        to_remove = []
        for vehicle_id, vehicle in self.vehicles.items():
            if vehicle.should_remove(self.frame_count, self.config):
                to_remove.append(vehicle_id)
                
        for vehicle_id in to_remove:
            del self.vehicles[vehicle_id]
            
    def check_violations(self):
        """Trả về list những xe bị vi phạm (dừng quá lâu)."""

        violations = []
        for vehicle in self.vehicles.values():
            if vehicle.check_violation(self.config):
                violations.append(vehicle)
        return violations

    def get_statistics(self):
        """Trả về thống kê tổng số xe, xe đang chạy, dừng, vi phạm."""

        total = len(self.vehicles)
        car_count = sum(1 for v in self.vehicles.values() if v.vehicle_class == 2)
        motorbike_count = sum(1 for v in self.vehicles.values() if v.vehicle_class == 3)
        
        moving = 0
        stopped = 0
        violations = 0
        
        for vehicle in self.vehicles.values():
            status = vehicle.get_effective_status()
            if status == 'moving':
                moving += 1
            elif status == 'stopped':
                stopped += 1
                # Nếu dừng quá lâu → tính là vi phạm
                if (vehicle.stop_start_time is not None and 
                    time.time() - vehicle.stop_start_time >= self.config.MAX_STOP_TIME_BEFORE_CAPTURE):
                    violations += 1
        
        return {
            'total': total,
            'cars': car_count,
            'motorbikes': motorbike_count,
            'moving': moving,
            'stopped': stopped,
            'violations': violations
        }
