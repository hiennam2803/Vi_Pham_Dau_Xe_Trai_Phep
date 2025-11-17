import cv2
import os
import datetime
import time
from pathlib import Path

from models.picturemodel import PictureModel
from map.location_store import get_location


DB_FILE = "pictures.txt"   # file lưu metadata


class CaptureManager:
    """Quản lý việc chụp và lưu lại ảnh vi phạm cũng như lưu metadata."""
    def __init__(self, config):
        self.config = config
        self.setup_capture_directory()
        
    def setup_capture_directory(self):
        capture_path = Path(self.config.CAPTURE_DIR)
        capture_path.mkdir(parents=True, exist_ok=True)

    def save_to_txt(self, picture: PictureModel):
        """Lưu metadata vào file txt, không in gì ra màn hình."""
        line = f"{picture.id}|{picture.image_path}|{picture.lat}|{picture.lon}|{picture.timestamp}\n"
        with open(DB_FILE, "a", encoding="utf-8") as f:
            f.write(line)

    def capture_violation(self, frame, vehicle, detections=None):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            vehicle_name = self.config.VEHICLE_NAMES.get(vehicle.vehicle_class, "Unknown")
            vehicle_name_clean = vehicle_name.replace(" ", "_")
            name_map = {"Xe_hoi": "Car", "Xe_may": "Motorbike"}
            vehicle_name_clean = name_map.get(vehicle_name_clean, vehicle_name_clean)

            if not hasattr(vehicle, 'last_box') or vehicle.last_box is None:
                return None

            x1, y1, x2, y2 = map(int, vehicle.last_box)
            x1 = max(0, x1); y1 = max(0, y1)
            x2 = min(frame.shape[1], x2); y2 = min(frame.shape[0], y2)

            # FULL FRAME
            if self.config.SAVE_FULL_FRAME:
                frame_copy = frame.copy()
                cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 0, 255), 3)

                filename = f"{vehicle.id}_{vehicle_name_clean}_{timestamp}.jpg"
                filepath = os.path.join(self.config.CAPTURE_DIR, filename)
                cv2.imwrite(filepath, frame_copy)
                vehicle.last_captured_filename = filename  # <-- Gán filename sau khi lưu ảnh full-frame

            # CROP
            else:
                if x2 <= x1 or y2 <= y1:
                    return None

                crop = frame[y1:y2, x1:x2]
                if crop.size == 0:
                    return None

                filename = f"violation_{vehicle.id}_{vehicle_name_clean}_{timestamp}.jpg"
                filepath = os.path.join(self.config.CAPTURE_DIR, filename)
                cv2.imwrite(filepath, crop)
                vehicle.last_captured_filename = filename  # <-- Gán filename sau khi lưu ảnh crop

            vehicle.mark_captured()

            lat, lon = get_location()

            picture = PictureModel(
                id=vehicle.id,
                image_path=filepath,
                lat=lat,
                lon=lon,
                timestamp=timestamp
            )

            self.save_to_txt(picture)
            return picture

        except:
            return None
