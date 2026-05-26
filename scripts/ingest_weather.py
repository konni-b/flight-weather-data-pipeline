"""
ingest_weather.py
-----------------
Fetches airport coordinates from BigQuery (staging.stg_airports),
retrieves daily weather data from the Meteostat API via RapidAPI,
and uploads the result to GCS as a JSON file.

GCS path convention:
    weather/raw/<year>/<month>/weather_<iata_code>_<year>_<month>.json

Run with:
    uv run python scripts/ingest_weather.py
"""

import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from google.cloud import bigquery, storage

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
API_KEY = os.getenv("METEOSTAT_KEY")
API_HOST = os.getenv("METEOSTAT_HOST")

URL = "https://meteostat.p.rapidapi.com/point/daily"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST,
}

AIRPORTS = ['ORD', 'MDW', 'DEN', 'DAL', 'HOU', 'BUF', 'BWI', 'LAS', 'PHX', 'ATL']

PERIODS = [
    ("2022-12-01", "2022-12-31", 2022, 12),
    ("2023-01-01", "2023-01-31", 2023, 1),
]

DATA_DIR = Path("data/weather")
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Fetch airport coordinates from BigQuery
# ---------------------------------------------------------------------------
def get_airport_coordinates() -> list:
    """Query stg_airports for lat/lon of the selected airports."""
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
        SELECT iata_code, latitude, longitude
        FROM `{PROJECT_ID}.staging.stg_airports`
        WHERE iata_code IN UNNEST({AIRPORTS})
    """
    airports = list(client.query(query).result())
    print(f"✅ Fetched coordinates for {len(airports)} airports from BigQuery")
    return airports


# ---------------------------------------------------------------------------
# Fetch weather data from Meteostat API
# ---------------------------------------------------------------------------
def fetch_weather(airport, start: str, end: str) -> list:
    """Fetch daily weather for one airport and one time period."""
    querystring = {
        "lat": airport.latitude,
        "lon": airport.longitude,
        "start": start,
        "end": end,
    }
    response = requests.get(URL, headers=HEADERS, params=querystring, timeout=30)
    response.raise_for_status()

    data = response.json().get("data", [])
    if not data:
        print(f"⚠️  No data returned for {airport.iata_code} ({start} to {end})")
        return []

    # Add airport identifier to each daily row
    for day in data:
        day["iata_code"] = airport.iata_code

    return data


# ---------------------------------------------------------------------------
# Upload to GCS
# ---------------------------------------------------------------------------
def upload_to_gcs(
    gcs_client: storage.Client,
    data: list,
    year: int,
    month: int,
) -> None:
    """Upload weather data as a JSON file to GCS."""
    filename = f"weather_{year}_{month:02d}.json"
    local_path = DATA_DIR / filename
    gcs_path = f"weather/raw/{year}/{month:02d}/{filename}"

    # Write locally first
    with open(local_path, "w") as f:
        for row in data:
            f.write(json.dumps(row) + '\n')

    # Upload to GCS
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)
    print(f"✨ Uploaded {len(data)} rows → gs://{BUCKET_NAME}/{gcs_path}")

    # Cleanup
    local_path.unlink()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    airports = get_airport_coordinates()
    gcs_client = storage.Client(project=PROJECT_ID)

    for start, end, year, month in PERIODS:
        print(f"\n{'='*50}")
        print(f"  Processing {year}-{month:02d}")
        print(f"{'='*50}")

        all_weather_data = []

        for airport in airports:
            print(f"⬇️  Fetching weather for {airport.iata_code} ({start} to {end})...")
            data = fetch_weather(airport, start, end)
            all_weather_data.extend(data)
            time.sleep(0.5)  # be polite to the API

        upload_to_gcs(gcs_client, all_weather_data, year, month)

    print("\n🎉 All done.")
