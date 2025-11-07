import numpy as np
from collections import defaultdict
from ..models.vehicle import Vehicle

class VehicleTracker:
    def __init__(self, config):
        self.config = config
        self.vehicles = {}
        self.next_id = 1
        self.frame_count = 0
        
    def calculate_iou(self, box1, box2):
        """Calculate IoU between two bounding boxes"""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Calculate intersection area
        x1_inter = max(x1_1, x1_2)
        y1_inter = max(y1_1, y1_2)
        x2_inter = min(x2_1, x2_2)
        y2_inter = min(y2_1, y2_2)
        
        if x2_inter <= x1_inter or y2_inter <= y1_inter:
            return 0
        
        inter_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)
        box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0
        
    def assign_vehicle_ids(self, current_detections):
        """Assign IDs to detected vehicles"""
        if not self.vehicles:
            # No existing tracks, assign new IDs to all
            assigned_detections = {}
            for cls, det in current_detections:
                assigned_detections[self.next_id] = (cls, det)
                self.next_id += 1
            return assigned_detections
            
        # Create IoU matrix
        iou_matrix = np.zeros((len(current_detections), len(self.vehicles)))
        for i, (_, det) in enumerate(current_detections):
            for j, (vehicle_id, vehicle) in enumerate(self.vehicles.items()):
                iou_matrix[i, j] = self.calculate_iou(det['box'], vehicle.last_box)
                
        # Assign IDs based on IoU
        assigned_detections = {}
        used_tracks = set()
        used_detections = set()
        
        # Find best matches (highest IoU)
        while True:
            max_iou = 0
            best_i, best_j = -1, -1
            
            for i in range(len(current_detections)):
                if i in used_detections:
                    continue
                for j in range(len(self.vehicles)):
                    if j in used_tracks:
                        continue
                    if iou_matrix[i, j] > max_iou:
                        max_iou = iou_matrix[i, j]
                        best_i, best_j = i, j
                        
            # Stop if no IoU > threshold
            if max_iou < self.config.IOU_THRESHOLD:
                break
                
            # Assign ID
            track_id = list(self.vehicles.keys())[best_j]
            assigned_detections[track_id] = current_detections[best_i]
            used_tracks.add(best_j)
            used_detections.add(best_i)
            
        # Assign new IDs to unassigned detections
        for i, (cls, det) in enumerate(current_detections):
            if i not in used_detections:
                assigned_detections[self.next_id] = (cls, det)
                self.next_id += 1
                
        return assigned_detections
        
    def update(self, current_detections):
        """Update vehicle tracking with new detections"""
        self.frame_count += 1
        
        # Assign IDs to current detections
        assigned_detections = self.assign_vehicle_ids(current_detections)
        
        # Update existing vehicles and create new ones
        for vehicle_id, (cls, detection) in assigned_detections.items():
            if vehicle_id not in self.vehicles:
                # Create new vehicle
                self.vehicles[vehicle_id] = Vehicle(
                    vehicle_id, cls, detection['box'], 
                    detection['center'], detection['confidence'], 
                    self.frame_count
                )
            else:
                # Update existing vehicle
                vehicle = self.vehicles[vehicle_id]
                vehicle.update(
                    detection['box'], detection['center'], 
                    detection['confidence'], self.frame_count
                )
                vehicle.calculate_movement(self.config)
                
        # Handle occlusion
        self._handle_occlusion()
        
        # Clean up old vehicles
        self._cleanup_vehicles()
        
        return assigned_detections
        
    def _handle_occlusion(self):
        """Handle vehicle occlusion"""
        for vehicle in self.vehicles.values():
            frames_since_last_seen = self.frame_count - vehicle.last_seen_frame
            
            # Mark as occluded if not seen for a while
            if frames_since_last_seen > 3 and not vehicle.is_occluded:
                vehicle.freeze_status()
                
            # Update frozen status frames
            if vehicle.is_occluded:
                vehicle.frozen_status_frames += 1
                
    def _cleanup_vehicles(self):
        """Remove old and low-confidence vehicles"""
        to_remove = []
        for vehicle_id, vehicle in self.vehicles.items():
            if vehicle.should_remove(self.frame_count, self.config):
                to_remove.append(vehicle_id)
                
        for vehicle_id in to_remove:
            del self.vehicles[vehicle_id]
            
    def get_statistics(self):
        """Get tracking statistics"""
        car_count = sum(1 for v in self.vehicles.values() if v.vehicle_class == 2)
        motorbike_count = sum(1 for v in self.vehicles.values() if v.vehicle_class == 3)
        
        moving_count = 0
        stopped_count = 0
        for vehicle in self.vehicles.values():
            effective_status = vehicle.get_effective_status()
            if effective_status == 'stopped' and vehicle.status_frames >= self.config.MIN_FRAMES_STOP:
                stopped_count += 1
            else:
                moving_count += 1
                
        occluded_count = sum(1 for v in self.vehicles.values() if v.is_occluded)
        
        return {
            'total': len(self.vehicles),
            'cars': car_count,
            'motorbikes': motorbike_count,
            'moving': moving_count,
            'stopped': stopped_count,
            'occluded': occluded_count
        }