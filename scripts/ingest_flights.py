"""
ingest_flights.py
-----------------
Downloads BTS On-Time Performance ZIP files, extracts the CSV,
uploads it to GCS under a structured path, then cleans up local files.

GCS path convention:
    flights/raw/<year>/<month>/<filename>.csv
"""

import argparse
import os
import zipfile
from pathlib import Path

import requests
from dotenv import load_dotenv
from google.cloud import storage

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

BTS_BASE_URL = "https://transtats.bts.gov/PREZIP"
CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB — BTS files are ~100 MB, stream in chunks


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------
def download_zip(year: int, month: int) -> Path:
    """Stream-download the BTS zip for a given year/month to a local file."""
    zip_name = (
        f"On_Time_Reporting_Carrier_On_Time_Performance_1987_present"
        f"_{year}_{month}.zip"
    )
    url = f"{BTS_BASE_URL}/{zip_name}"
    local_zip_path = DATA_DIR / zip_name

    print(f"⬇️  Downloading {year}-{month:02d} from BTS...")
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()  # raises on 4xx/5xx — no silent failures

    with open(local_zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)

    size_mb = local_zip_path.stat().st_size / 1_000_000
    print(f"✅ Downloaded {zip_name} ({size_mb:.1f} MB)")
    return local_zip_path


def extract_csv(local_zip_path: Path) -> Path:
    """Extract the first (and usually only) CSV from the BTS zip."""
    with zipfile.ZipFile(local_zip_path, "r") as zf:
        csv_files = [f for f in zf.namelist() if f.endswith(".csv")]
        if not csv_files:
            raise ValueError(f"No CSV found inside {local_zip_path.name}")
        csv_filename = csv_files[0]
        zf.extract(csv_filename, path=DATA_DIR)

    local_csv_path = DATA_DIR / csv_filename
    print(f"📦 Extracted: {csv_filename}")
    return local_csv_path


def upload_to_gcs(
    client: storage.Client,
    local_csv_path: Path,
    year: int,
    month: int,
) -> None:
    """Upload CSV to GCS under a structured path and log the destination URI."""
    gcs_path = f"flights/raw/{year}/{month:02d}/{local_csv_path.name}"
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(gcs_path)

    print(f"🚀 Uploading to gs://{BUCKET_NAME}/{gcs_path} ...")
    blob.upload_from_filename(local_csv_path)
    print(f"✨ Upload complete → gs://{BUCKET_NAME}/{gcs_path}")


def process(year: int, month: int, client: storage.Client, keep_local: bool) -> None:
    """Full pipeline for one year/month: download → extract → upload → cleanup."""
    local_zip_path = None
    local_csv_path = None
    try:
        local_zip_path = download_zip(year, month)
        local_csv_path = extract_csv(local_zip_path)
        upload_to_gcs(client, local_csv_path, year, month)
    finally:
        if not keep_local:
            for path in [local_zip_path, local_csv_path]:
                if path and path.exists():
                    path.unlink()
                    print(f"🗑️  Deleted local file: {path.name}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest BTS flight data to GCS"
    )
    parser.add_argument(
        "--keep-local",
        action="store_true",
        help="Keep local ZIP and CSV files after upload (default: delete them)",
    )
    args = parser.parse_args()

    # Initialise GCS client once — reused across all downloads
    gcs_client = storage.Client(project=PROJECT_ID)

    # The story arc: Dec 2022 (the meltdown) + Jan 2023 (the recovery)
    tasks = [
        (2022, 12),
        (2023, 1),
    ]

    for year, month in tasks:
        print(f"\n{'='*50}")
        print(f"  Processing {year}-{month:02d}")
        print(f"{'='*50}")
        process(year, month, gcs_client, keep_local=args.keep_local)

    print("\n🎉 All done.")
