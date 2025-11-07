import numpy as np
from ..models.vehicle import Vehicle

class VehicleTracker:
    def __init__(self, config):
        self.config = config
        self.vehicles = {}
        self.next_id = 1
        self.frame_count = 0

    def calculate_iou(self, box1, box2):
        """Tính IoU giữa hai bounding box"""
        x1, y1 = max(box1[0], box2[0]), max(box1[1], box2[1])
        x2, y2 = min(box1[2], box2[2]), min(box1[3], box2[3])
        if x2 <= x1 or y2 <= y1:
            return 0
        inter = (x2 - x1) * (y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        return inter / (area1 + area2 - inter + 1e-6)

    def assign_vehicle_ids(self, detections):
        """Gán ID cho các phát hiện"""
        if not self.vehicles:
            assigned = {self.next_id + i: det for i, det in enumerate(detections)}
            self.next_id += len(detections)
            return assigned

        iou_matrix = np.array([[self.calculate_iou(det[1]['box'], v.last_box)
                               for v in self.vehicles.values()] for det in detections])

        assigned, used_det, used_track = {}, set(), set()
        while True:
            max_idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
            max_iou = iou_matrix[max_idx]
            if max_iou < self.config.IOU_THRESHOLD:
                break
            i, j = max_idx
            vid = list(self.vehicles.keys())[j]
            assigned[vid] = detections[i]
            used_det.add(i)
            used_track.add(j)
            iou_matrix[i, :] = -1
            iou_matrix[:, j] = -1

        # Gán ID mới cho phát hiện chưa dùng
        for i, det in enumerate(detections):
            if i not in used_det:
                assigned[self.next_id] = det
                self.next_id += 1
        return assigned

    def update(self, detections):
        """Cập nhật theo khung hình mới"""
        self.frame_count += 1
        assigned = self.assign_vehicle_ids(detections)

        for vid, (cls, det) in assigned.items():
            if vid not in self.vehicles:
                self.vehicles[vid] = Vehicle(vid, cls, det['box'], det['center'], det['confidence'], self.frame_count)
            else:
                v = self.vehicles[vid]
                v.update(det['box'], det['center'], det['confidence'], self.frame_count)
                v.calculate_movement(self.config)

        self._handle_occlusion()
        self._cleanup_vehicles()
        return assigned

    def _handle_occlusion(self):
        """Xử lý xe bị che khuất"""
        for v in self.vehicles.values():
            if self.frame_count - v.last_seen_frame > 3:
                if not v.is_occluded:
                    v.freeze_status()
                v.frozen_status_frames += 1

    def _cleanup_vehicles(self):
        """Xóa xe cũ hoặc kém tin cậy"""
        self.vehicles = {vid: v for vid, v in self.vehicles.items()
                         if not v.should_remove(self.frame_count, self.config)}

    def get_statistics(self):
        """Thống kê trạng thái xe"""
        cars = sum(v.vehicle_class == 2 for v in self.vehicles.values())
        bikes = sum(v.vehicle_class == 3 for v in self.vehicles.values())
        stopped = sum(v.get_effective_status() == 'stopped' and v.status_frames >= self.config.MIN_FRAMES_STOP
                      for v in self.vehicles.values())
        moving = len(self.vehicles) - stopped
        occluded = sum(v.is_occluded for v in self.vehicles.values())

        return {
            'total': len(self.vehicles),
            'cars': cars,
            'motorbikes': bikes,
            'moving': moving,
            'stopped': stopped,
            'occluded': occluded
        }
