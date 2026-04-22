# config.py

# OpenRice API configuration
BASE_URL = "https://www.openrice.com/api/pois"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.openrice.com/zh/hongkong/restaurants",
}

# Districts to scrape
# Yuen Long = 3003
# North District on OpenRice is split into Sheung Shui (3001) and Fanling (3008)
DISTRICTS = {
    "yuen_long": {"id": 3003, "name_en": "Yuen Long", "name_zh": "元朗"},
    "sheung_shui": {"id": 3001, "name_en": "Sheung Shui", "name_zh": "上水"},
    "fanling": {"id": 3008, "name_en": "Fanling", "name_zh": "粉嶺"},
}

# Request settings
REQUEST_TIMEOUT = 15
SLEEP_BETWEEN_REQUESTS = 0.5  # seconds
MAX_RETRIES = 3

# Output
OUTPUT_CSV = "restaurants.csv"
