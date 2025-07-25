```python
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# URL của trang web mục tiêu
URL = "https://lichcupdien.app/huyen-hon-quan/"

# Đường dẫn file JSON lưu trữ dữ liệu trước đó
PREVIOUS_DATA_FILE = "previous_outage_data.json"

# Thông tin gửi email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")  # Lấy từ biến môi trường
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")  # Lấy từ biến môi trường
RECEIVER_EMAIL = "huyhau2004@gmail.com"  # Thay bằng email người nhận

def scrape_outage_data():
    """Lấy dữ liệu lịch cúp điện từ trang web."""
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Tìm các phần tử chứa thông tin cúp điện (cần điều chỉnh theo cấu trúc HTML thực tế)
        outage_data = []
        sections = soup.find_all('div')  # Giả định các mục lịch nằm trong thẻ div
        for section in sections:
            text = section.get_text()
            if "Tân Hưng" in text:
                # Giả định định dạng: ngày, thời gian, khu vực, lý do
                date = text.split("Ngày:")[1].split("\n")[0].strip() if "Ngày:" in text else ""
                time = text.split("Thời gian: Từ:")[1].split("Đến:")[0].strip() + " - " + text.split("Đến:")[1].strip() if "Thời gian: Từ:" in text else ""
                area = "Xã Tân Hưng"
                outage_data.append({"date": date, "time": time, "area": area})

        return outage_data
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu: {e}")
        return []

def load_previous_data():
    """Đọc dữ liệu lịch cúp điện trước đó từ file JSON."""
    try:
        if os.path.exists(PREVIOUS_DATA_FILE):
            with open(PREVIOUS_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Lỗi khi đọc dữ liệu trước đó: {e}")
        return []

def save_current_data(data):
    """Lưu dữ liệu hiện tại vào file JSON."""
    try:
        with open(PREVIOUS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu: {e}")

def compare_data(current_data, previous_data):
    """So sánh dữ liệu hiện tại với dữ liệu trước đó."""
    return current_data != previous_data

def send_email(changed_data):
    """Gửi email thông báo với thông tin lịch cúp điện."""
    try:
        msg = MIMEText(
            "Thông báo lịch cúp điện mới tại xã Tân Hưng:\n\n" +
            "\n".join([f"- Nơi cúp điện: {entry['area']}\n  Thời gian: {entry['time']} ngày {entry['date']}" 
                       for entry in changed_data])
        )
        msg['Subject'] = "Cập nhật lịch cúp điện xã Tân Hưng"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("Email đã được gửi!")
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")

def main():
    # Lấy dữ liệu mới
    current_data = scrape_outage_data()
    
    # Đọc dữ liệu trước đó
    previous_data = load_previous_data()
    
    # So sánh dữ liệu
    if compare_data(current_data, previous_data):
        print("Phát hiện thay đổi trong lịch cúp điện!")
        send_email(current_data)
        save_current_data(current_data)
    else:
        print("Không có thay đổi trong lịch cúp điện.")

if __name__ == "__main__":
    main()
```
