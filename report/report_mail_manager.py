import smtplib
import ssl
from email.message import EmailMessage
import os

class ReportMailManager:
    def __init__(self, sender_email, app_password, receiver_email):
        self.sender_email = sender_email
        self.app_password = app_password
        self.receiver_email = receiver_email

    def send_violation_report(self, image_path):
        """Gửi email chứa hình ảnh vi phạm"""
        if not os.path.exists(image_path):
            print(f"Lỗi: Không tìm thấy ảnh để gửi: {image_path}")
            return False

        try:
            msg = EmailMessage()
            msg['Subject'] = "Phát hiện xe vi phạm"
            msg['From'] = self.sender_email
            msg['To'] = self.receiver_email
            msg.set_content("Hệ thống phát hiện xe vi phạm. Hình ảnh xe vi phạm.")

            # Đính kèm hình ảnh
            with open(image_path, 'rb') as f:
                img_data = f.read()

            msg.add_attachment(
                img_data,
                maintype='image',
                subtype='jpeg',
                filename=os.path.basename(image_path)
            )

            # Gửi mail qua Gmail SMTP
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.sender_email, self.app_password)
                server.send_message(msg)

            print(f"Đã gửi email thành công tới {self.receiver_email}")
            return True
        
        except Exception as e:
            print("Lỗi khi gửi email:", e)
            return False
