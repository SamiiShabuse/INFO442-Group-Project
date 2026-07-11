# Notebooks Folder

This folder is organized by the project pipeline.

## Folder Structure

- `01_source_data/`
  - `fred/`
  - `wikipedia/`
  - `yfinance/`
- `02_integration/`
- `03_features/`
- `04_modeling/`

## Pipeline Order

1. Run the source-specific notebooks in `01_source_data/` to acquire, clean, and explore each data source.
2. Run `02_integration/01_data_integration.ipynb` to combine the cleaned source data.
3. Run `03_features/01_feature_engineering.ipynb` to create the model-ready dataset.
4. Run the notebooks in `04_modeling/` to train and compare models.

If code becomes important and reusable, move it into the `src/` folder so the project is easier to rerun and share.
