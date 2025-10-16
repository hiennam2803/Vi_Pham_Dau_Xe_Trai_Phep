# Vi_Pham_Dau_Xe_Trai_Phep

Xây dựng Ứng dụng xử lý Vi Phạm Đậu xe Trái Phép

Tên chủ đề:
Xây dựng Ứng dụng Vi phạm Đậu xe Trái phép
1. Mô tả tổng quan về chủ đề:
  Ứng dụng được lập trình bằng Python, có chức năng phát hiện và ghi nhận phương tiện đậu hoặc dừng quá thời gian cho phép (trên 3 phút) tại các khu vực cấm đậu xe.
  Hệ thống sử dụng camera giám sát kết hợp với mô hình trí tuệ nhân tạo YOLO (You Only Look Once) để nhận diện và theo dõi các phương tiện trong khung hình theo thời gian thực.
  Khi một xe bị phát hiện dừng liên tục trong hơn 3 phút, hệ thống sẽ ghi lại hình ảnh bằng camera, lưu thông tin biển số, thời gian và vị trí, sau đó thông báo vi phạm.
2. Lý do chọn chủ đề:
  Vấn đề đậu xe sai quy định gây ùn tắc giao thông và mất mỹ quan đô thị, đặc biệt tại các tuyến đường nội thành đông đúc.
  Giúp hỗ trợ lực lượng chức năng giám sát giao thông một cách tự động, chính xác và tiết kiệm nhân lực.
    Kết hợp giữa xử lý hình ảnh, trí tuệ nhân tạo và IoT, mang tính thực tế và ứng dụng cao trong đô thị thông minh.
Củng cố và áp dụng các kiến thức về Python, OpenCV, và mô hình học sâu (deep learning) đã học vào một bài toán thực tế.
3. Các bước cần thực hiện:
  Thu thập dữ liệu:
    Dữ liệu hình ảnh và video về các phương tiện giao thông (xe máy, ô tô) tại các khu vực cấm đậu.
  Huấn luyện mô hình nhận diện:
    Sử dụng YOLOv8 (mô hình nhận diện vật thể hiện đại, tốc độ cao).
    Tinh chỉnh (fine-tune) để phát hiện các đối tượng là phương tiện giao thông.
  Theo dõi và xác định thời gian dừng xe:
    Kết hợp YOLO với thuật toán theo dõi (Tracking) như DeepSORT hoặc ByteTrack để theo dõi từng phương tiện theo thời gian.
    Đo thời gian mà mỗi xe đứng yên trong cùng một vị trí (≥ 3 phút).
  Phát hiện và ghi nhận vi phạm:
    Khi phát hiện xe dừng quá 3 phút → chụp khung hình, lưu lại video hoặc ảnh, biển số, thời gian, vị trí.
  Giao diện và thông báo:
    Hiển thị cảnh báo trên giao diện (console hoặc web nhỏ).
    Có thể mở rộng để gửi thông báo đến cơ quan chức năng hoặc lưu log tự động.
4. Mô hình và công nghệ sử dụng:
  Mô hình AI: YOLOv8 (You Only Look Once version 8)
  Thư viện: OpenCV, Ultralytics YOLO, NumPy, time, collections
  Ngôn ngữ lập trình: Python
  Thuật toán theo dõi: DeepSORT / ByteTrack
  Thiết bị: Camera giám sát hoặc video mẫu

Viphamdauxe/
├── src/
│   ├── main.py
│   └── ui.py
│   └── counter180s.py
├── data/
│   └── images/ ("type bike"_"id"_"time".png)
│   └── data/ ("id".txt)
├── test/
│   └── videotest1.mp4
│   └── videotest2.mp4
└── README.md
