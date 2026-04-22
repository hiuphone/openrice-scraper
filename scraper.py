# scraper.py
"""
OpenRice Hong Kong restaurant scraper.
Scrapes name, latitude, longitude, and opening hours for restaurants
in Yuen Long and North District (Sheung Shui + Fanling).
"""

import csv
import json
import time
from datetime import datetime

import requests

from config import (
    BASE_URL,
    DISTRICTS,
    HEADERS,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    SLEEP_BETWEEN_REQUESTS,
    OUTPUT_CSV,
)


def fetch_page(district_id: int, page: int) -> dict | None:
    """Fetch a single page of restaurant results from the OpenRice API."""
    params = {
        "uiLang": "zh",
        "uiCity": "hongkong",
        "page": page,
        "sortBy": "Default",
        "districtId": district_id,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(
                BASE_URL,
                headers=HEADERS,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
            if "searchResult" not in data:
                print(f"  Unexpected response keys: {list(data.keys())}")
                return None
            return data
        except requests.exceptions.RequestException as e:
            print(f"  Request error (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(2 * attempt)
            else:
                return None


def format_opening_hours(poi_hours: list[dict]) -> str:
    """
    Convert the raw poiHours array into a human-readable string.

    Example output:
        Mon-Fri: 07:00-01:30; Sat-Sun: 08:00-02:00
    """
    if not poi_hours:
        return ""

    day_names = {
        1: "Mon",
        2: "Tue",
        3: "Wed",
        4: "Thu",
        5: "Fri",
        6: "Sat",
        7: "Sun",
    }

    # Build a map day_of_week -> formatted hours string
    day_hours = {}
    for entry in poi_hours:
        dow = entry.get("dayOfWeek")
        if dow is None:
            continue

        if entry.get("isClose"):
            hours_str = "Closed"
        elif entry.get("is24hr"):
            hours_str = "24hr"
        else:
            start = entry.get("period1Start", "")
            end = entry.get("period1End", "")
            # Remove seconds if present (e.g. "07:00:00" -> "07:00")
            if start and len(start) > 5:
                start = start[:5]
            if end and len(end) > 5:
                end = end[:5]
            hours_str = f"{start}-{end}" if start and end else ""

        day_hours[dow] = hours_str

    # Group consecutive days with identical hours
    groups = []
    current_start = None
    current_end = None
    current_hours = None

    for dow in range(1, 8):
        hours = day_hours.get(dow, "")
        if current_hours is None or hours != current_hours:
            if current_hours is not None:
                groups.append((current_start, current_end, current_hours))
            current_start = dow
            current_end = dow
            current_hours = hours
        else:
            current_end = dow

    if current_hours is not None:
        groups.append((current_start, current_end, current_hours))

    # Format groups
    parts = []
    for start_dow, end_dow, hours in groups:
        if start_dow == end_dow:
            day_label = day_names.get(start_dow, str(start_dow))
        else:
            day_label = f"{day_names.get(start_dow, str(start_dow))}-{day_names.get(end_dow, str(end_dow))}"
        parts.append(f"{day_label}: {hours}")

    return "; ".join(parts)


def extract_restaurant_data(raw: dict) -> dict:
    """Extract the fields we care about from a single API result object."""
    name = raw.get("nameUI") or raw.get("name") or ""
    name_en = raw.get("nameOtherLang") or ""

    address = ""
    address_obj = raw.get("addressUI")
    if isinstance(address_obj, dict):
        address = address_obj.get("plainAddress", "").strip()

    lat = raw.get("mapLatitude")
    lon = raw.get("mapLongitude")
    url = raw.get("urlUI", "")

    district_obj = raw.get("district", {})
    district_name = district_obj.get("name", "")

    poi_hours = raw.get("poiHours", [])
    opening_hours = format_opening_hours(poi_hours)

    return {
        "name_zh": name,
        "name_en": name_en,
        "district": district_name,
        "address": address,
        "latitude": lat,
        "longitude": lon,
        "opening_hours": opening_hours,
        "url": f"https://www.openrice.com{url}"
        if url and not url.startswith("http")
        else url,
    }


def scrape_district(district_key: str, district_info: dict) -> list[dict]:
    """Scrape all restaurants for a single district."""
    district_id = district_info["id"]
    district_name = district_info["name_en"]
    print(f"\nScraping {district_name} (districtId={district_id})...")

    restaurants = []
    page = 1
    empty_count = 0

    while True:
        data = fetch_page(district_id, page)
        if data is None:
            print(f"  Failed to fetch page {page}. Stopping.")
            break

        results = data["searchResult"]["paginationResult"]["results"]
        if not results:
            empty_count += 1
            if empty_count >= 2:
                print(f"  Empty page {page}. Finished.")
                break
        else:
            empty_count = 0
            for raw in results:
                restaurants.append(extract_restaurant_data(raw))

        print(
            f"  Page {page}: fetched {len(results)} restaurants (total {len(restaurants)})"
        )

        if not results:
            break

        page += 1
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    return restaurants


def save_to_csv(all_restaurants: list[dict], filename: str) -> None:
    """Write the collected data to a CSV file."""
    if not all_restaurants:
        print("No restaurants to save.")
        return

    fieldnames = [
        "name_zh",
        "name_en",
        "district",
        "address",
        "latitude",
        "longitude",
        "opening_hours",
        "url",
    ]

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_restaurants)

    print(f"\nSaved {len(all_restaurants)} restaurants to {filename}")


def main():
    print("OpenRice Scraper started at", datetime.now().isoformat())

    all_restaurants = []
    for key, info in DISTRICTS.items():
        district_restaurants = scrape_district(key, info)
        all_restaurants.extend(district_restaurants)

    save_to_csv(all_restaurants, OUTPUT_CSV)
    print("Scraper finished at", datetime.now().isoformat())


if __name__ == "__main__":
    main()
