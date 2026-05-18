"""
load_flights_to_bq.py
---------------------
Loads raw flights CSVs from GCS into BigQuery (raw.flights table).
Covers Dec 2022 (the meltdown) and Jan 2023 (the recovery).

Run with:
    uv run python scripts/load_flights_to_bq.py
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
TABLE = "flights"
DESTINATION = f"{PROJECT_ID}.{DATASET}.{TABLE}"

URIS = [
    f"gs://{BUCKET_NAME}/flights/raw/2022/12/*.csv",
    f"gs://{BUCKET_NAME}/flights/raw/2023/01/*.csv",
]

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
def load_to_bigquery() -> None:
    client = bigquery.Client(project=PROJECT_ID)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  # skip header row
        autodetect=True,      # infer column types automatically
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # replace table on re-run
    )

    print(f"⬆️  Loading flights data into {DESTINATION}...")
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
