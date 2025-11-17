class PictureModel:
    """Đại diện một bức ảnh chụp vi phạm và métadữ liệu liên quan."""
    def __init__(self, id, image_path, lat, lon, timestamp):
        self.id = id
        self.image_path = image_path
        self.lat = lat
        self.lon = lon
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "id": self.id,
            "image": self.image_path,
            "lat": self.lat,
            "lon": self.lon,
            "time": self.timestamp
        }
