"""
load_weather_to_bq.py
---------------------
Loads raw weather JSONs from GCS into BigQuery (raw.weather table).
Covers Dec 2022 (the meltdown) and Jan 2023 (the recovery).

Run with:
    uv run python scripts/load_weather_to_bq.py
"""

import os
from dotenv import load_dotenv
from google.cloud import bigquery

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

DATASET = "raw"
TABLE = "weather"
DESTINATION = f"{PROJECT_ID}.{DATASET}.{TABLE}"

URIS = [
    f"gs://{BUCKET_NAME}/weather/raw/2022/12/*.json",
    f"gs://{BUCKET_NAME}/weather/raw/2023/01/*.json",
]

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
def load_to_bigquery() -> None:
    client = bigquery.Client(project=PROJECT_ID)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,      # infer column types automatically
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # replace table on re-run
    )

    print(f"⬆️  Loading weather data into {DESTINATION}...")
    print(f"   Sources: {URIS}")

    load_job = client.load_table_from_uri(
        URIS,
        DESTINATION,
        job_config=job_config,
    )

    load_job.result()  # wait for the job to finish

    table = client.get_table(DESTINATION)
    print(f"✅ Done — {table.num_rows:,} rows loaded into {DESTINATION}")


if __name__ == "__main__":
    load_to_bigquery()
