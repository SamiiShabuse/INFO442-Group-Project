# Data Folder

This folder is for the datasets used in the project.

Put raw and cleaned data here, such as:

- Historical stock and ETF price data from Yahoo Finance or `yfinance`
- Benchmark data like SPY
- Sector labels for each ticker
- Risk-free rate data from FRED
- Cleaned datasets used for modeling and dashboard charts

We will try to keep raw data and cleaned data separate when possible. For example:

- `raw/` for original downloaded files
- `processed/` for cleaned or feature-ready files

Within `processed/`, source-specific cleaned files live under `source_data/`:

- `processed/source_data/yfinance/`
- `processed/source_data/wikipedia/`
- `processed/source_data/fred/`

Project-level outputs such as integrated datasets, feature-engineered datasets, and model results live directly under `processed/` in their own folders.

Do not put notebooks, code, reports, or dashboard files in this folder.
