import smtplib
import ssl
from email.message import EmailMessage
import os
import models.picturemodel

class ReportMailManager:
    """Quản lý gửi email báo cáo vi phạm"""
    def __init__(self, sender_email, app_password, receiver_email):
        """Khởi tạo đối tượng gửi mail với thông tin tài khoản gửi và nhận"""
        self.sender_email = sender_email
        self.app_password = app_password
        self.receiver_email = receiver_email

    def send_violation_report(self, image_path, picture):
        """Gửi email báo cáo vi phạm với ảnh và thông tin mô tả xe vi phạm"""
        if not os.path.exists(image_path):
            print(f"Lỗi: Không tìm thấy ảnh để gửi: {image_path}")
            return False
        try:
            msg = EmailMessage()
            msg['Subject'] = "Phát hiện xe vi phạm"
            msg['From'] = self.sender_email
            msg['To'] = self.receiver_email

            mail_text = "Xin chào,\n\nHệ thống đã phát hiện một xe vi phạm và đính kèm hình ảnh vi phạm.\n"
            # Bổ sung thông tin vi phạm bằng trường của picture
            if picture is not None:
                mail_text += f"- ID xe: {picture.id}\n"
                mail_text += f"- Thời gian: {picture.timestamp}\n"
                mail_text += f"- Toạ độ GPS: ({picture.lat}, {picture.lon})\n"
            mail_text += "\nTrân trọng,\nHệ thống giám sát giao thông\n"
            msg.set_content(mail_text)

            with open(image_path, 'rb') as f:
                img_data = f.read()
            msg.add_attachment(
                img_data,
                maintype='image',
                subtype='jpeg',
                filename=os.path.basename(image_path)
            )
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.sender_email, self.app_password)
                server.send_message(msg)
            print(f"Đã gửi email thành công tới {self.receiver_email}")
            return True
        except Exception as e:
            print("Lỗi khi gửi email:", e)
            return False