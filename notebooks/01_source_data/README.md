# Source Data Notebooks

This folder contains notebooks for each original data source.

## Folders

- `fred/` acquires, preprocesses, and explores FRED macroeconomic and risk data.
- `wikipedia/` acquires, preprocesses, and explores S&P 500 metadata.
- `yfinance/` acquires, preprocesses, and explores market data from Yahoo Finance.

Run these notebooks before integration. They write cleaned source outputs to `data/processed/source_data/`.

Because these notebooks are three levels below the repository root, their data paths use `../../../data/...`.
