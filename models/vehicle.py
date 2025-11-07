from collections import deque
import numpy as np

class Vehicle:
    def __init__(self, vehicle_id, vehicle_class, detection_box, center, confidence, frame_count):
        self.id = vehicle_id
        self.vehicle_class = vehicle_class
        self.positions = deque([center], maxlen=30)
        self.last_box = detection_box
        self.center = center
        self.status = 'unknown'
        self.status_frames = 0
        self.speed_history = deque(maxlen=10)
        self.moving_frames = 0
        self.last_update = frame_count
        self.confidence_history = deque([confidence], maxlen=10)
        self.total_detections = 1
        self.last_seen_frame = frame_count
        self.is_occluded = False
        self.frozen_status = None
        self.frozen_status_frames = 0
        
    def update(self, detection_box, center, confidence, frame_count):
        """Update vehicle with new detection"""
        self.positions.append(center)
        self.last_box = detection_box
        self.center = center
        self.last_update = frame_count
        self.last_seen_frame = frame_count
        self.confidence_history.append(confidence)
        self.total_detections += 1
        
        # Reset occlusion if reappeared
        if self.is_occluded:
            self.is_occluded = False
            self.frozen_status = None
            self.frozen_status_frames = 0
            
    def calculate_movement(self, config):
        """Calculate movement metrics and update status"""
        if len(self.positions) >= 2:
            last_pos = np.array(self.positions[-1])
            prev_pos = np.array(self.positions[-2])
            inst_dist = np.linalg.norm(last_pos - prev_pos)
            self.speed_history.append(inst_dist)
            
        # Calculate distances for recent frames
        distances = []
        if len(self.positions) >= 3:
            start = max(1, len(self.positions) - 3)
            for i in range(start, len(self.positions)):
                current_pos = np.array(self.positions[i])
                previous_pos = np.array(self.positions[i-1])
                distance = np.linalg.norm(current_pos - previous_pos)
                distances.append(distance)
                
        avg_distance = np.mean(distances) if distances else 0
        max_distance = np.max(distances) if distances else 0
        
        # Calculate recent speed
        recent_speeds = list(self.speed_history)[-3:]
        avg_recent_speed = np.mean(recent_speeds) if recent_speeds else 0
        
        # Update moving frames counter
        if avg_recent_speed >= config.MOVE_THRESHOLD:
            self.moving_frames += 1
        else:
            self.moving_frames = 0
            
        # Determine status
        if self.moving_frames >= config.MIN_FRAMES_MOVE:
            self.status = 'moving'
            self.status_frames = 0
        else:
            if avg_distance < config.STOP_THRESHOLD and max_distance < config.STOP_THRESHOLD * 2:
                self.status_frames += 1
                if self.status_frames >= config.MIN_FRAMES_STOP:
                    self.status = 'stopped'
                    
    def get_effective_status(self):
        """Get the effective status for display/counting"""
        if self.is_occluded and self.frozen_status is not None:
            return self.frozen_status
        return self.status
        
    def freeze_status(self):
        """Freeze current status when occluded"""
        self.is_occluded = True
        self.frozen_status = self.status
        self.frozen_status_frames = self.status_frames
        
    def should_remove(self, frame_count, config):
        """Check if vehicle should be removed from tracking"""
        frames_since_last_update = frame_count - self.last_update
        avg_confidence = np.mean(list(self.confidence_history)) if self.confidence_history else 0
        
        is_too_old = frames_since_last_update > config.MAX_TRACK_AGE
        is_occluded_too_long = self.is_occluded and (frame_count - self.last_seen_frame) > config.OCCLUSION_THRESHOLD
        is_missing_too_long = (frame_count - self.last_seen_frame) > int(config.MISSING_SECONDS * 30)  # Assuming 30 FPS
        is_low_confidence = avg_confidence < config.MIN_TRACK_CONFIDENCE and self.total_detections > 5
        has_few_detections = self.total_detections < config.MIN_DETECTIONS_TO_KEEP and frames_since_last_update > 10
        
        return ((is_too_old and not self.is_occluded) or is_missing_too_long or 
                is_occluded_too_long or is_low_confidence or has_few_detections)