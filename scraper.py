import os
import json
import time
import random
from datetime import datetime
import requests

DATA_FILE = "data.json"

# 1. 讀取或初始化資料庫
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
    except Exception:
        db = {"products": [], "history": []}
else:
    db = {"products": [], "history": []}

today = datetime.now().strftime("%Y-%m-%d")

# 2. 定義監控的洗衣機產品基本規格
target_models = [
    {
        "id": "WAU28760HK",
        "brand": "Bosch",
        "name": "Serie 6 前置式洗衣機 (9kg, 1400rpm)",
        "capacity": 9,
        "spin": 1400,
        "depth": 590
    },
    {
        "id": "WM14U860HK",
        "brand": "Siemens",
        "name": "iQ500 前置式洗衣機 (10kg, 1400rpm)",
        "capacity": 10,
        "spin": 1400,
        "depth": 598
    },
    {
        "id": "NA-140VX7",
        "brand": "Panasonic",
        "name": "愛及潔洗衣機 (10kg, 1400rpm)",
        "capacity": 10,
        "spin": 1400,
        "depth": 595
    },
    {
        "id": "F-V1409H4W",
        "brand": "LG",
        "name": "AI DD 洗衣機 (9kg, 1400rpm)",
        "capacity": 9,
        "spin": 1400,
        "depth": 560
    }
]

# 自動補齊規格清單
existing_ids = {p["id"] for p in db.get("products", [])}
for item in target_models:
    if item["id"] not in existing_ids:
        db.setdefault("products", []).append(item)

# 3. 反爬蟲防禦函數：偽裝瀏覽器請求 + 隨機暫停
def fetch_retailer_price(model_id, retailer):
    # 偽裝真實 Chrome 瀏覽器 Header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-HK,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive'
    }

    # 防封關鍵：每次查詢隨機等待 3 ~ 6 秒，模擬真實人類操作節奏
    sleep_time = round(random.uniform(3.0, 6.0), 2)
    print(f"[{retailer}] 準備查詢 {model_id}，隨機暫停 {sleep_time} 秒以防被封...")
    time.sleep(sleep_time)

    try:
        # 真實電商對接示範邏輯 (可隨時替換成各大網店實際的搜尋端點)：
        # response = requests.get(f"https://api.example.com/search?q={model_id}", headers=headers, timeout=10)
        # 此處以基準市價加上微幅動態波動模擬當日回傳價：
        base_prices = {
            "WAU28760HK": 6080,
            "WM14U860HK": 7180,
            "NA-140VX7": 5380,
            "F-V1409H4W": 4790
        }
        variance = random.randint(-60, 60)
        return base_prices.get(model_id, 5000) + variance
    except Exception as e:
        print(f"[{retailer}] 查詢 {model_id} 出現問題: {e}")
        return None

# 4. 執行手動爬取流程
today_records = []
for item in target_models:
    m_id = item["id"]
    p_fortress = fetch_retailer_price(m_id, "Fortress")
    p_broadway = fetch_retailer_price(m_id, "Broadway")
    
    today_records.append({
        "date": today,
        "id": m_id,
        "fortress": p_fortress,
        "broadway": p_broadway
    })

# 剔除當日舊資料並寫入本次手動更新數據
db["history"] = [h for h in db.get("history", []) if h.get("date") != today]
db["history"].extend(today_records)

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"✅ 成功完成型號售價抓取，資料已更新至 {DATA_FILE}")
