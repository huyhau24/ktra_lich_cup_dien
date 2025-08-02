import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

URL = "https://lichcupdien.app/huyen-hon-quan/"
PREVIOUS_DATA_FILE = "previous_data.json"
RUN_FLAG_FILE = "run_flag.json"

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

        print(f"📦 Dữ liệu lấy được: {len(results)} mục")
        return results
    except Exception as e:
        print("❌ Lỗi lấy dữ liệu:", e)
        return []

def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    today_str = datetime.now().strftime("%Y-%m-%d")

    run_flag = load_json(RUN_FLAG_FILE, {})
    if run_flag.get("last_run_date") == today_str:
        print("✅ Hôm nay đã xử lý, không gửi lại.")
        return

    current_data = scrape_outage_data()
    previous_data = load_json(PREVIOUS_DATA_FILE, [])

    if not current_data:
        print("❌ Không có dữ liệu mới.")
        return

    if current_data != previous_data:
        print("🆕 Có thay đổi, cập nhật file.")
        save_json(PREVIOUS_DATA_FILE, current_data)
    else:
        print("✅ Dữ liệu giống cũ, không cập nhật.")

    save_json(RUN_FLAG_FILE, {"last_run_date": today_str})

if __name__ == "__main__":
    main()
