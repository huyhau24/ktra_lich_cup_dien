import requests
from bs4 import BeautifulSoup
import json
import os
import smtplib
from email.mime.text import MIMEText

# URL của trang web mục tiêu
URL = "https://lichcupdien.app/huyen-hon-quan/"

# File lưu dữ liệu trước đó
PREVIOUS_DATA_FILE = "previous_outage_data.json"

# Thông tin email (sử dụng biến môi trường)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = "huyhau2004@gmail.com"

def scrape_outage_data():
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        # Tìm tất cả các mục thông báo lịch cúp điện
        items = soup.find_all("li", class_="item-data-search-province")
        for item in items:
            text_all = item.get_text()
            if "Tân Hưng" not in text_all:
                continue

            day = item.find("p", class_="item-properties-data-search-province-day")
            time_tags = item.find_all("p", class_="item-properties-data-search-province-time-start")
            area = item.find_all("p", class_="item-properties-data-search-province-reason")

            result = {
                "date": day.get_text(strip=True) if day else "",
                "time": f"{time_tags[0].get_text(strip=True)} - {time_tags[1].get_text(strip=True)}" if len(time_tags) >= 2 else "",
                "area": area[0].get_text(strip=True) if area else ""
            }
            results.append(result)
        return results
    except Exception as e:
        print("Lỗi khi lấy dữ liệu:", e)
        return []

def load_previous_data():
    if os.path.exists(PREVIOUS_DATA_FILE):
        with open(PREVIOUS_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_current_data(data):
    with open(PREVIOUS_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def compare_data(current, previous):
    return current != previous

def send_email(data):
    try:
        content = "🔌 **Lịch cúp điện mới tại xã Tân Hưng:**\n\n"
        for d in data:
            content += f"- 📅 Ngày: {d['date']}\n"
            content += f"  ⏰ Thời gian: {d['time']}\n"
            content += f"  📍 Khu vực: {d['area']}\n\n"
        content += "🔗 Xem chi tiết tại: https://lichcupdien.app/huyen-hon-quan/"

        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = "🔔 Cập nhật lịch cúp điện xã Tân Hưng"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

        print("✅ Email đã được gửi.")
    except Exception as e:
        print("❌ Lỗi khi gửi email:", e)

def main():
    current_data = scrape_outage_data()
    previous_data = load_previous_data()

    if compare_data(current_data, previous_data):
        print("🔄 Phát hiện thay đổi lịch cúp điện.")
        send_email(current_data)
        save_current_data(current_data)
    else:
        print("✅ Không có thay đổi trong lịch cúp điện.")

if __name__ == "__main__":
    main()
