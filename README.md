# openrice-scraper

Python web scraper for OpenRice Hong Kong restaurant data (names, coordinates, opening hours).

## What it does

Scrapes restaurant information from the OpenRice internal API for specified Hong Kong districts:
- **Name** (Chinese and English when available)
- **Latitude & Longitude**
- **Opening hours** (formatted as human-readable ranges, e.g. `Mon-Fri: 07:00-01:30; Sat-Sun: 08:00-02:00`)
- **District**, **address**, and **OpenRice URL**

## Prerequisites

This project uses [uv](https://docs.astral.sh/uv/) for Python dependency management.

### Install uv

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For other methods (Homebrew, pip, etc.), see the [official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

## Installation

Clone the repo, then sync dependencies:

```bash
uv sync
```

This creates a virtual environment and installs `requests` (the only runtime dependency).

## Usage

### 1. Scrape default districts

Edit `config.py` to set which districts to scrape, then run:

```bash
uv run python scraper.py
```

Output is saved to `restaurants.csv`.

### 2. Change districts

Districts are defined in `config.py` under `DISTRICTS`. A reference list of all 99 districts is provided in `districts.json`. To scrape a different district, copy its entry from `districts.json` into `config.py`:

```python
DISTRICTS = {
    "central": {"id": 1003, "name_en": "Central", "name_zh": "中環"},
    "mong_kok": {"id": 2010, "name_en": "Mong Kok", "name_zh": "旺角"},
}
```

Then run `uv run python scraper.py` again.

### 3. Regenerate the district list

If OpenRice updates their district definitions, regenerate `districts.json`:

```bash
uv run python fetch_districts.py
```

This fetches the latest district IDs and names directly from the OpenRice API.

## Output format

`restaurants.csv` contains the following columns:

| Column | Description |
|--------|-------------|
| `name_zh` | Chinese name |
| `name_en` | English name (if available) |
| `district` | District name |
| `address` | Full address |
| `latitude` | Latitude |
| `longitude` | Longitude |
| `opening_hours` | Formatted opening hours |
| `url` | OpenRice page URL |

## Default districts

By default, the scraper targets:
- **Yuen Long** (元朗) — districtId `3003`
- **Sheung Shui** (上水) — districtId `3001`
- **Fanling** (粉嶺) — districtId `3008`

These cover the Yuen Long and North District areas of Hong Kong.

## Notes

- The scraper uses the OpenRice internal API (`/api/pois`).
- Rate limiting: requests are spaced `0.5s` apart by default (configurable in `config.py`).
- The API returns 15 results per page; pagination continues until no more results are returned.
- Some restaurants may have missing opening hours or English names.
