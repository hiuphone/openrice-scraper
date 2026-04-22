import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.openrice.com/zh/hongkong/restaurants",
}

# Fetch Chinese data
url = (
    "https://www.openrice.com/api/pois?uiLang=zh&uiCity=hongkong&page=1&sortBy=Default"
)
r = requests.get(url, headers=headers, timeout=15)
data = r.json()

locations = data["searchResult"]["refineSearchFilter"]["locations"]

# Filter only actual districts (exclude landmarks, MTR stations, malls)
districts = []
for loc in locations:
    search_key = loc.get("searchKey", "")
    if not search_key.startswith("districtId="):
        continue
    alias = loc.get("aliasUI", "")
    name_zh = alias.split("||")[0] if "||" in alias else loc["name"]
    districts.append(
        {
            "id": int(loc["queryValue"]),
            "name_en": loc["name"],
            "name_zh": name_zh,
            "count": loc.get("count", 0),
            "searchKey": search_key,
        }
    )

# Fetch English names
url_en = (
    "https://www.openrice.com/api/pois?uiLang=en&uiCity=hongkong&page=1&sortBy=Default"
)
r_en = requests.get(url_en, headers=headers, timeout=15)
data_en = r_en.json()
locations_en = data_en["searchResult"]["refineSearchFilter"]["locations"]
en_names = {}
for loc in locations_en:
    if loc.get("searchKey", "").startswith("districtId="):
        en_names[int(loc["queryValue"])] = loc["name"]

for d in districts:
    d["name_en"] = en_names.get(d["id"], d["name_en"])

districts.sort(key=lambda x: x["id"])

with open("districts.json", "w", encoding="utf-8") as f:
    json.dump(districts, f, ensure_ascii=False, indent=2)

print("Saved " + str(len(districts)) + " districts to districts.json")
for d in districts:
    line = (
        "  "
        + str(d["id"])
        + ": "
        + d["name_en"]
        + " / "
        + d["name_zh"]
        + " ("
        + str(d["count"])
        + " restaurants)"
    )
    print(line)
