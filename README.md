# SF Bike Theft

Analysis of bicycle theft in San Francisco using SFPD incident report data from DataSF.

## Setup

    uv sync

## Layout

- `data/` — raw and processed data (not committed; regenerate with `scripts/`)
- `notebooks/` — exploratory analysis
- `src/sf_bike_theft/` — reusable code
- `scripts/` — data download / pipeline entrypoints
- `reports/figures/` — exported charts