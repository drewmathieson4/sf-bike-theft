# SF Bike Theft

Analysis of bicycle theft in San Francisco using SFPD incident report data from DataSF.  

This is mostly an exploratory data analysis focused on attempting to make causal statements about bike theft in sf (or explaining why we can't).

## Setup

    uv sync

## Layout

- `data/` — raw and processed data (not committed; regenerate with `scripts/`)
- `notebooks/` — exploratory analysis
- `src/sf_bike_theft/` — reusable code
- `scripts/` — data download / pipeline entrypoints
- `reports/figures/` — exported charts