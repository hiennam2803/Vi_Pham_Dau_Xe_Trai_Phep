import cv2
import numpy as np

class Visualizer:
    def __init__(self, config):
        self.config = config
        
    def draw_vehicles(self, frame, vehicles, assigned_detections):
        """Draw vehicles and information on frame"""
        for vehicle_id, vehicle in vehicles.items():
            # Get display information
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
                    
            # Determine color and label
            vehicle_name = self.config.VEHICLE_NAMES.get(cls, "Xe khac")
            effective_status = vehicle.get_effective_status()
            
            # Determine color based on status
            if effective_status == 'stopped' and vehicle.status_frames >= self.config.MIN_FRAMES_STOP:
                color = (0, 255, 0)  # green = stopped
                if vehicle.is_occluded:
                    status_text = "DA DUNG (CHE KHUAT)"
                else:
                    status_text = "DA DUNG"
            else:
                color = (0, 0, 255)  # red = moving
                if vehicle.is_occluded and effective_status == 'moving':
                    status_text = "DI CHUYEN (CHE KHUAT)"
                else:
                    status_text = "DI CHUYEN"
                    
            # Draw bounding box and information
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Display detailed information
            avg_confidence = np.mean(list(vehicle.confidence_history)) if vehicle.confidence_history else 0
            label = f"ID:{vehicle_id} {vehicle_name} ({avg_confidence:.2f})"
            cv2.putText(frame, label, (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.putText(frame, status_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw trail
            if len(vehicle.positions) > 1:
                points = np.array(vehicle.positions, dtype=np.int32)
                cv2.polylines(frame, [points], False, color, 2)
                
    def draw_statistics(self, frame, stats):
        """Draw statistics on frame"""
        cv2.putText(frame, f"Tong: {stats['total']}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Xe hoi: {stats['cars']}", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(frame, f"Xe may: {stats['motorbikes']}", (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(frame, f"Di chuyen: {stats['moving']}", (10, 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, f"Da dung: {stats['stopped']}", (10, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Bi che khuat: {stats['occluded']}", (10, 180), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
        
        # Instructions
        cv2.putText(frame, "Nhan 'q' de thoat", (10, frame.shape[0] - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)