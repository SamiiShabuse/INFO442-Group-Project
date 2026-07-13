# Processed Data

This folder contains cleaned and derived project datasets.

## Folder Structure

- `source_data/`
  - Cleaned source-specific files from FRED, Wikipedia, and Yahoo Finance.
- `integrated/`
  - Combined datasets produced by `notebooks/02_integration/01_data_integration.ipynb`.
- `features/`
  - Feature-engineered modeling dataset produced by `notebooks/03_features/01_feature_engineering.ipynb`.
- `modeling/`
  - Saved model predictions and metrics from `notebooks/04_modeling/`.

Use `source_data/` for cleaned individual data sources. Use the other folders for project-level outputs that combine or model across sources.
