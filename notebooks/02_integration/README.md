# Integration Notebooks

This folder contains notebooks that combine cleaned source datasets into project-level datasets.

## Current Notebook

- `01_data_integration.ipynb`

This notebook reads from:

- `data/processed/source_data/yfinance/`
- `data/processed/source_data/wikipedia/`
- `data/processed/source_data/fred/`

It writes to:

- `data/processed/integrated/`

Run this after the source data notebooks and before feature engineering.
