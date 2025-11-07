# Vi Phạm Đậu Xe Trái Phép (CarCheck)

Ứng dụng Python phát hiện, theo dõi và ghi nhận phương tiện đậu/dừng trái phép dựa trên mô hình YOLOv8. Hệ thống chạy thời gian thực, hiển thị trực quan ngay trên khung hình và cung cấp giao diện đồ họa đơn giản để chọn nguồn vào.

---

## 1. Tổng quan dự án
- **Mục tiêu**: Tự động phát hiện các phương tiện (ô tô, xe máy) dừng hoặc đỗ tại khu vực cấm trong thời gian dài, hỗ trợ lực lượng chức năng xử lý vi phạm.
- **Công nghệ lõi**: Ultralytics YOLOv8 dùng cho phát hiện đối tượng; thuật toán gán ID dựa trên IoU để theo dõi và xác định trạng thái di chuyển/dừng.
- **Môi trường**: Ưu tiên Python trên Windows, nhưng có thể triển khai trên Linux/macOS với các phụ thuộc tương thích.
- **Đầu ra dự kiến**: Khung hình có khung bao phương tiện, trạng thái (đang dừng/di chuyển), đường đi, thống kê tổng quan và khả năng mở rộng để chụp/lưu bằng chứng.

---

## 2. Kiến trúc & cấu trúc thư mục

```
Vi_Pham_Dau_Xe_Trai_Phep/
├── README.md
└── src/
    ├── main.py                # Điểm vào chính, khởi chạy GUI
    ├── gui.py                 # Giao diện Tkinter (chọn nguồn, Start/Stop)
    ├── config.py              # Tham số cấu hình cho phát hiện & theo dõi
    ├── capture/               # (để trống) dự kiến chứa logic ghi dữ liệu/video
    ├── reportAPI/             # (để trống) dự kiến tích hợp API báo cáo
    ├── models/
    │   ├── detection_model.py # Bao bọc YOLOv8, lọc và chuẩn hóa kết quả
    │   └── vehicle.py         # Định nghĩa lớp Vehicle, trạng thái di chuyển
    ├── tracker/
    │   └── vehicle_tracker.py # Quản lý các track, gán ID, xử lý che khuất
    └── utils/
        └── visualizer.py      # Vẽ khung, nhãn, trail, thống kê lên frame
```

> **Ghi chú**: Thư mục `capture/` và `reportAPI/` hiện chưa có mã. Được giữ lại để mở rộng chức năng lưu bằng chứng và gửi báo cáo.

---

## 3. Luồng hoạt động chính
1. **Khởi động GUI** (`main.py` → `gui.py`)
   - Người dùng nhập nguồn (`0` cho webcam) hoặc duyệt chọn video.
   - Bấm **Start** để chạy pipeline; **Stop** để dừng tiến trình đang chạy.

2. **Phát hiện & theo dõi**
   - `DetectionModel.detect_vehicles()` gọi YOLOv8 (`ultralytics`) để trả về danh sách bounding box cho lớp 2 (car) và 3 (motorbike).
   - `VehicleTracker` gán ID, tính toán IoU để nối track, cập nhật trạng thái khi phương tiện bị che khuất hoặc biến mất.

3. **Hiển thị**
   - `Visualizer` vẽ khung, nhãn, trạng thái (`DI CHUYEN`, `DA DUNG`, ...), đường đi và thống kê tổng hợp (tổng số, số xe theo loại, số đang dừng, bị che khuất) trên frame.

4. **Cấu hình linh hoạt** (`config.py`)
   - Tất cả ngưỡng tốc độ, số khung hình tối thiểu, ngưỡng IoU, ngưỡng tin cậy theo lớp... được định nghĩa tại đây để dễ tinh chỉnh.

---

## 4. Yêu cầu hệ thống
- Python **3.9 – 3.11** (các bản mới hơn cần kiểm tra thêm với Ultralytics)
- Windows 10/11 (đã thử); Linux/macOS cần cài đặt thêm driver camera tương thích
- GPU là **không bắt buộc** nhưng nên dùng nếu cần xử lý thời gian thực độ phân giải cao
- Tối thiểu 4 GB RAM

---

## 5. Cài đặt & thiết lập môi trường

### 5.1. Tạo môi trường ảo (khuyến nghị)
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate    # Linux/macOS
```

### 5.2. Cài đặt phụ thuộc chính
```bash
pip install ultralytics opencv-python numpy
```

### 5.3. Kiểm tra mô hình
- Lần đầu chạy, Ultralytics sẽ tự tải `yolov8n.pt` (~6 MB).
- Nếu muốn dùng mô hình tùy chỉnh, đặt đường dẫn trong khi khởi tạo `DetectionModel(model_path=...)`.

---

## 6. Chạy ứng dụng

### 6.1. Khởi chạy GUI (cách mặc định)
```bash
python src/main.py
```

**Hướng dẫn:**
- Ô nhập nguồn chấp nhận `0` (webcam mặc định) hoặc đường dẫn đến file video (`C:\path\to\video.mp4`).
- Nút **Chọn file...** sử dụng hộp thoại hệ thống để chọn video.
- Nhấn **Start** để khởi chạy pipeline trong tiến trình mới.
- Nhấn **Stop** để gửi tín hiệu dừng tiến trình.

> **Quan trọng:** `gui.py` hiện tạo lệnh `python -m Viphamdauxe.main --source <nguồn>`. Trong repo chưa có package `Viphamdauxe` cũng như tham số `--source`. Để chạy thành công, cần:
> - Chỉnh lệnh trong `gui.py` về script thực tế của bạn,
> - Hoặc bổ sung module `Viphamdauxe.main` tương thích.

### 6.2. Chạy không GUI (tùy biến)
- Repo chưa cung cấp script CLI. Bạn có thể xây dựng pipeline riêng bằng cách kết hợp `DetectionModel`, `VehicleTracker` và `Visualizer` trong script mới.
- Gợi ý:
  1. Mở video bằng OpenCV (`cv2.VideoCapture`).
  2. Lặp từng frame, chạy `detect_vehicles`, `update`, `visualizer.draw_vehicles`.
  3. Dùng `cv2.imshow` để xem và `cv2.waitKey` để thoát.

---

## 7. Cấu hình chi tiết (`src/config.py`)

| Thuộc tính | Mô tả | Giá trị mặc định |
|------------|-------|-------------------|
| `MOVE_THRESHOLD` | Ngưỡng tốc độ (pixel/frame) để coi là di chuyển | `1` |
| `STOP_THRESHOLD` | Ngưỡng dịch chuyển trung bình để coi là dừng | `1.5` |
| `MIN_FRAMES_STOP` | Số khung liên tiếp dưới ngưỡng để khẳng định dừng | `15` |
| `MIN_FRAMES_MOVE` | Số khung liên tiếp trên ngưỡng để khẳng định di chuyển | `5` |
| `CONFIDENCE_THRESHOLD` | Ngưỡng tin cậy mặc định | `0.3` |
| `VEHICLE_CONFIDENCE_THRESHOLDS` | Ngưỡng riêng cho cls 2/3 | `{2: 0.5, 3: 0.35}` |
| `MIN_BOX_AREA/WIDTH/HEIGHT` | Lọc bounding box nhỏ/ảo | `500 / 20 / 20` |
| `IOU_THRESHOLD` | Ngưỡng IoU để nối track | `0.4` |
| `MAX_TRACK_AGE` | Track biến mất quá số khung này thì xóa | `60` |
| `MIN_TRACK_CONFIDENCE` | Loại track tin cậy thấp | `0.4` |
| `MIN_DETECTIONS_TO_KEEP` | Track ít lần phát hiện thì bỏ | `3` |
| `OCCLUSION_THRESHOLD` | Số khung bị che khuất trước khi loại | `45` |
| `MISSING_SECONDS` | Thời gian tối đa không thấy lại (giây) | `60` |
| `VEHICLE_NAMES` | Map mã lớp → tên hiển thị | `{2: "Xe hoi", 3: "Xe may"}` |

Điều chỉnh các giá trị này để phù hợp với đặc thù camera (góc quay, FPS, độ phân giải).

---

## 8. Mở rộng & roadmap đề xuất
- **Pipeline CLI**: Bổ sung module dùng trực tiếp kiểu `python -m carcheck --source video.mp4` để GUI có thể gọi.
- **Lưu bằng chứng**: Ghi hình khi phát hiện vi phạm vào `src/capture/`, đính kèm ảnh/crop biển số, thời gian.
- **Nhận diện biển số**: Tích hợp thư viện OCR hoặc model chuyên dụng để đọc biển số.
- **API báo cáo**: Hoàn thiện thư mục `reportAPI/` nhằm gửi cảnh báo qua REST/WebSocket.
- **Cấu hình GUI nâng cao**: Cho phép chỉnh ngưỡng, chọn model, bật/tắt lưu bằng chứng ngay trong giao diện.
- **Benchmark**: Ghi log FPS, thời gian xử lý mỗi frame, số lượng track trung bình.
- **Triển khai thực tế**: Đóng gói thành dịch vụ Windows hoặc container Docker.

---

## 9. Kiểm thử & gỡ lỗi
- **Kiểm thử nhanh**: Dùng webcam với nguồn `0` để đảm bảo GUI hoạt động.
- **Video test**: Nếu có video sẵn, chạy để quan sát hiển thị; đảm bảo FPS ổn định.
- **Log**: Thêm log tạm trong `vehicle_tracker.py` hoặc `visualizer.py` để theo dõi trạng thái ID, số khung dừng.
- **Lỗi thường gặp**:
  - *ModuleNotFoundError: Viphamdauxe*: Sửa đường dẫn trong `gui.py`.
  - *CV2 error: can't open camera*: Kiểm tra quyền truy cập webcam, thử với video.
  - *Ultralytics không tải model*: Kiểm tra kết nối Internet hoặc tải thủ công `yolov8n.pt` về và đặt đường dẫn đầy đủ.

---

## 10. Tài liệu tham khảo
- [Ultralytics YOLOv8 Docs](https://docs.ultralytics.com/)
- [OpenCV VideoCapture](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html)
- [Tkinter documentation](https://docs.python.org/3/library/tkinter.html)

---

## 11. Đóng góp
- Fork dự án, tạo nhánh riêng cho thay đổi.
- Đảm bảo mô tả rõ ràng trong Pull Request: mục tiêu, thay đổi, cách kiểm thử.
- Gợi ý tiêu chí review: tốc độ xử lý, độ chính xác, UX GUI, khả năng mở rộng.

---

## 12. Giấy phép
Chưa chỉ định. Nếu bạn muốn công bố, hãy bổ sung thông tin giấy phép (ví dụ MIT, GPL) vào đây và tạo file `LICENSE` tương ứng.

---

## 13. Liên hệ
- Nhóm/Người phát triển: (bổ sung tên/email/số liên hệ nếu muốn)
- Vấn đề kỹ thuật: tạo issue hoặc gửi email cho quản trị dự án.

---

> Tài liệu này nhằm cung cấp cái nhìn toàn diện về dự án hiện tại và định hướng phát triển. Cập nhật README khi bổ sung module mới để mọi người dễ dàng theo dõi.
