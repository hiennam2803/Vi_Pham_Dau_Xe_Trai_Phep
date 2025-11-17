import os

latitude = None
longitude = None

# Lưu trữ và truy vấn vị trí GPS cho hệ thống
def set_location(lat, lon):
    global latitude, longitude
    latitude = lat
    longitude = lon

    # Lưu vị trí vào file text trong thư mục map
    location_file_path = os.path.join(os.path.dirname(__file__), "location.txt")
    with open(location_file_path, "w") as file:
        file.write(f"{lat},{lon}")

def get_location():
    # Đọc vị trí từ file text trong thư mục map nếu tồn tại
    location_file_path = os.path.join(os.path.dirname(__file__), "location.txt")
    if os.path.exists(location_file_path):
        with open(location_file_path, "r") as file:
            data = file.read().strip()
            lat, lon = map(float, data.split(","))
            return lat, lon

    return latitude, longitude
