import requests
from bs4 import BeautifulSoup
import json
import os
import smtplib
from email.mime.text import MIMEText

# URL của trang web mục tiêu
URL = "https://lichcupdien.app/huyen-hon-quan/"

# Đường dẫn file lưu dữ liệu trước đó
PREVIOUS_DATA_FILE = "previous_outage_data.json"

# Thông tin email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = "huyhau2004@gmail.com"  # Thay bằng email người nhận

def scrape_outage_data():
    """Lấy dữ liệu lịch cúp điện từ trang web."""
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Danh sách lưu thông tin cúp điện không trùng
        outage_data = []
        seen_texts = set()

        divs = soup.find_all('div')
        for div in divs:
            text = div.get_text(separator='\n').strip()

            if "Tân Hưng" in text and text not in seen_texts:
                seen_texts.add(text)

                # Lấy ngày
                if "Ngày:" in text:
                    date = text.split("Ngày:")[1].split("\n")[0].strip()
                else:
                    date = ""

                # Lấy thời gian
                if "Thời gian: Từ:" in text and "Đến:" in text:
                    try:
                        start = text.split("Thời gian: Từ:")[1].split("Đến:")[0].strip()
                        end = text.split("Đến:")[1].split("\n")[0].strip()
                        time = f"{start} - {end}"
                    except:
                        time = ""
                else:
                    time = ""

                area = "Xã Tân Hưng"

                outage_data.append({
                    "date": date,
                    "time": time,
                    "area": area
                })

        return outage_data
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu: {e}")
        return []

def load_previous_data():
    try:
        if os.path.exists(PREVIOUS_DATA_FILE):
            with open(PREVIOUS_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Lỗi khi đọc dữ liệu trước đó: {e}")
        return []

def save_current_data(data):
    try:
        with open(PREVIOUS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu: {e}")

def compare_data(current, previous):
    return current != previous

def send_email(changed_data):
    try:
        content = "🔌 **Thông báo lịch cúp điện mới tại xã Tân Hưng:**\n\n"
        for entry in changed_data:
            content += f"- Ngày: {entry['date']}\n  Thời gian: {entry['time']}\n  Khu vực: {entry['area']}\n\n"

        msg = MIMEText(content)
        msg['Subject'] = "Cập nhật lịch cúp điện xã Tân Hưng"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

        print("✅ Email đã được gửi!")
    except Exception as e:
        print(f"❌ Lỗi khi gửi email: {e}")

def main():
    current_data = scrape_outage_data()
    previous_data = load_previous_data()

    if compare_data(current_data, previous_data):
        print("🔁 Phát hiện thay đổi trong lịch cúp điện.")
        send_email(current_data)
        save_current_data(current_data)
    else:
        print("✅ Không có thay đổi.")

if __name__ == "__main__":
    main()
