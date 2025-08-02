import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# --- CẤU HÌNH ---
URL = "https://lichcupdien.app/huyen-hon-quan/"
PREVIOUS_DATA_FILE = "previous_data.json"
RUN_FLAG_FILE = "run_flag.json"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = "huyhau2004@gmail.com"

# --- HÀM LẤY DỮ LIỆU TỪ WEB ---
def scrape_outage_data():
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        items = soup.find_all("li", class_="item-data-search-province")
        for item in items:
            if "Tân Khai" not in item.get_text():
                continue

            day = item.find("p", class_="item-properties-data-search-province-day")
            time_tags = item.find_all("p", class_="item-properties-data-search-province-time-start")
            area = item.find_all("p", class_="item-properties-data-search-province-reason")

            results.append({
                "date": day.get_text(strip=True) if day else "",
                "time": f"{time_tags[0].get_text(strip=True)} - {time_tags[1].get_text(strip=True)}" if len(time_tags) >= 2 else "",
                "area": area[0].get_text(strip=True) if area else ""
            })

        return results
    except Exception as e:
        print("❌ Lỗi lấy dữ liệu:", e)
        return []

# --- HÀM GỬI EMAIL ---
def send_email(data):
    try:
        content = "🔌 Lịch cúp điện mới tại xã Tân Hưng:\n\n"
        for d in data:
            content += f"- 📅 Ngày: {d['date']}\n"
            content += f"  ⏰ Thời gian: {d['time']}\n"
            content += f"  📍 Khu vực: {d['area']}\n\n"
        content += f"🔗 Xem chi tiết: {URL}"

        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = "🔔 Cập nhật lịch cúp điện xã Tân Hưng"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ Email đã gửi.")
    except Exception as e:
        print("❌ Lỗi gửi email:", e)

# --- HỖ TRỢ ĐỌC/GHI FILE JSON ---
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- HÀM CHÍNH ---
def main():
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    current_hour = now.hour

    # 1. Nếu chưa đến 8h sáng, không chạy
    if current_hour < 8:
        print("⏰ Chưa đến 8h sáng, không kiểm tra.")
        return

    # 2. Nếu đã xử lý hôm nay rồi → không làm gì
    run_flag = load_json(RUN_FLAG_FILE)
    if run_flag.get("last_run_date") == today_str:
        print("✅ Hôm nay đã xử lý, không gửi lại.")
        return

    # 3. Tiến hành kiểm tra dữ liệu mới
    current_data = scrape_outage_data()
    previous_data = load_json(PREVIOUS_DATA_FILE)
    
    # Nếu không có previous_data thì khởi tạo lần đầu
    if not previous_data:
        print("🆕 Chưa có dữ liệu cũ, tạo mới và không gửi email.")
        save_json(PREVIOUS_DATA_FILE, current_data)
        save_json(RUN_FLAG_FILE, {"last_run_date": today_str})
        return

    # 4. Nếu có thay đổi và có mục chứa Tân Hưng → gửi
    if current_data and current_data != previous_data:
        print("🔁 Có thay đổi dữ liệu & có Tân Hưng, gửi email.")
        send_email(current_data)
        save_json(PREVIOUS_DATA_FILE, current_data)
    else:
        print("✅ Không có cập nhật mới hoặc không có Tân Hưng.")

    # 5. Cập nhật cờ đã xử lý hôm nay
    save_json(RUN_FLAG_FILE, {"last_run_date": today_str})

if __name__ == "__main__":
    main()
