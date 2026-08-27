"""Collapse raw SFPD bike-theft reports into one row per theft event.

Implements the "Cleaning decisions" cell in notebooks/01_explore_raw.ipynb.

Input:   data/raw/sfpd_bike_thefts.csv       one row per report x incident code
Output:  data/processed/bike_thefts.csv      one row per incident_number

Run:     uv run python -m sf_bike_theft.clean
Import:  from sf_bike_theft.clean import load_clean
"""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "sfpd_bike_thefts.csv"
CLEAN_CSV = PROJECT_ROOT / "data" / "processed" / "bike_thefts.csv"

DATE_COLS = ["incident_datetime", "report_datetime"]

# Lowest to highest. Ordering these lets "max" mean "most valuable bike reported".
VALUE_BANDS = [
    "Theft, Bicycle, Att.",
    "Theft, Bicycle, <$50, no serial number",
    "Theft, Bicycle, <$50, serial number known",
    "Theft, Bicycle, $50-$200",
    "Theft, Bicycle, $200-$950",
    "Theft, Bicycle, >$950",
]
ATTEMPTED = "Theft, Bicycle, Att."


def load_raw(path: Path = RAW_CSV) -> pd.DataFrame:
    """Read the raw download with dates parsed. No cleaning."""
    return pd.read_csv(path, parse_dates=DATE_COLS + ["incident_date"])


def collapse_cases(raw: pd.DataFrame) -> pd.DataFrame:
    """One row per incident_number, following the survivorship rules."""
    df = raw.sort_values(["incident_number", "report_datetime"])  # earliest report first

    df["incident_description"] = pd.Categorical(
        df["incident_description"], categories=VALUE_BANDS, ordered=True
    )
    df["filed_online"] = df["filed_online"].eq(True)  # NaN means "not filed online"

    # groupby().first()/last() skip nulls, so a location missing on the initial
    # report is recovered from a later supplement if one has it.
    cases = (
        df.groupby("incident_number", sort=False)
        .agg(
            incident_datetime=("incident_datetime", "first"),
            report_datetime=("report_datetime", "first"),
            incident_description=("incident_description", "max"),
            resolution=("resolution", "last"),
            intersection=("intersection", "first"),
            analysis_neighborhood=("analysis_neighborhood", "first"),
            police_district=("police_district", "first"),
            latitude=("latitude", "first"),
            longitude=("longitude", "first"),
            filed_online=("filed_online", "any"),
            n_reports=("incident_id", "nunique"),
        )
        .reset_index()
    )
    return cases


def add_derived(cases: pd.DataFrame) -> pd.DataFrame:
    """Columns computed from the collapsed case, not present in the raw data."""
    cases = cases.copy()
    cases["attempted_theft"] = cases["incident_description"] == ATTEMPTED
    cases["has_location"] = cases["latitude"].notna()
    cases["report_lag_days"] = (cases["report_datetime"] - cases["incident_datetime"]).dt.days
    return cases


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    return add_derived(collapse_cases(raw))


def load_clean(path: Path = CLEAN_CSV) -> pd.DataFrame:
    """Read the processed file with the dtypes CSV can't remember."""
    df = pd.read_csv(path, parse_dates=DATE_COLS)
    df["incident_description"] = pd.Categorical(
        df["incident_description"], categories=VALUE_BANDS, ordered=True
    )
    return df


def main() -> None:
    raw = load_raw()
    cases = clean(raw)

    assert cases["incident_number"].is_unique, "dedupe failed: repeated incident_number"
    assert len(cases) == raw["incident_number"].nunique()

    CLEAN_CSV.parent.mkdir(parents=True, exist_ok=True)
    cases.to_csv(CLEAN_CSV, index=False)
    print(f"{len(raw):,} raw rows -> {len(cases):,} theft events -> {CLEAN_CSV.relative_to(PROJECT_ROOT)}")
    print(f"  attempted: {cases['attempted_theft'].sum():,}   no location: {(~cases['has_location']).sum():,}"
          f"   multi-report cases: {(cases['n_reports'] > 1).sum():,}")


if __name__ == "__main__":
    main()
