"""
Download SFPD bicycle-theft incident reports from DataSF into data/raw/.

Source:  Police Department Incident Reports: 2018 to Present
         https://data.sfgov.org/d/wg3w-h783
Filter:  incident_subcategory = 'Larceny Theft - Bicycle'
Output:  data/raw/sfpd_bike_thefts.csv        one row per incident report
         data/raw/sfpd_bike_thefts.meta.json  what was fetched, and when

Run from anywhere:  uv run scripts/download_data.py

data/raw/ is gitignored. DataSF refreshes the dataset daily; re-run this
script to pull the latest copy. Nothing here transforms the data.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

DATASET_ID = "wg3w-h783"
API_URL = f"https://data.sfgov.org/resource/{DATASET_ID}.json"
SUBCATEGORY = "Larceny Theft - Bicycle"
PAGE_SIZE = 50_000  # the most rows Socrata will return in one request

# Resolve paths relative to this file, not the current working directory,
# so the script behaves the same no matter which folder you run it from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUT_CSV = RAW_DIR / "sfpd_bike_thefts.csv"
OUT_META = RAW_DIR / "sfpd_bike_thefts.meta.json"


def fetch_all_rows() -> list[dict]:
    """Page through the Socrata API until it hands back a short page."""
    headers = {}
    # Optional. An app token lifts DataSF's anonymous rate limit; a ~4k-row
    # pull doesn't need one. To use one: export SODA_APP_TOKEN=... in your shell.
    if token := os.environ.get("SODA_APP_TOKEN"):
        headers["X-App-Token"] = token

    rows: list[dict] = []
    offset = 0
    while True:
        params = {
            "$where": f"incident_subcategory = '{SUBCATEGORY}'",
            "$order": ":id",  # a stable sort, so pages never overlap or skip rows
            "$limit": PAGE_SIZE,
            "$offset": offset,
        }
        response = requests.get(API_URL, params=params, headers=headers, timeout=60)
        response.raise_for_status()  # raise an exception on HTTP 4xx / 5xx
        page = response.json()
        rows.extend(page)
        print(f"  fetched {len(page):,} rows (running total {len(rows):,})")
        if len(page) < PAGE_SIZE:
            return rows  # a short page means we've reached the end
        offset += PAGE_SIZE


def main() -> None:
    print(f"Downloading '{SUBCATEGORY}' from DataSF dataset {DATASET_ID} ...")
    rows = fetch_all_rows()
    if not rows:
        raise SystemExit("No rows returned - check the filter or the API.")

    df = pd.DataFrame(rows)
    # `point` is a nested JSON object that duplicates latitude/longitude and
    # can't sit in a CSV cell. Everything else is kept exactly as returned.
    df = df.drop(columns=["point"], errors="ignore")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)

    meta = {
        "source_url": f"https://data.sfgov.org/d/{DATASET_ID}",
        "filter": f"incident_subcategory = '{SUBCATEGORY}'",
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rows": len(df),
        "columns": list(df.columns),
        "incident_date_min": df["incident_date"].min(),
        "incident_date_max": df["incident_date"].max(),
    }
    OUT_META.write_text(json.dumps(meta, indent=2))

    print(
        f"Wrote {len(df):,} rows x {df.shape[1]} columns -> {OUT_CSV.relative_to(PROJECT_ROOT)}"
    )
    print(
        f"Incident dates {meta['incident_date_min'][:10]} to {meta['incident_date_max'][:10]}"
    )


if __name__ == "__main__":
    main()
