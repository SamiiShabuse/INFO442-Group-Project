# Notebooks Folder

This folder contains the main project workflow, organized in the order the pipeline should be run.

## Folder Structure

```text
notebooks/
  01_source_data/
    fred/
    wikipedia/
    yfinance/
  02_integration/
  03_features/
  04_modeling/
```

## Run Order

1. `01_source_data/`
   - Acquire, clean, and explore the source datasets.
   - Outputs cleaned source data to `data/processed/source_data/`.
2. `02_integration/01_data_integration.ipynb`
   - Combines cleaned Yahoo Finance, Wikipedia, and FRED data.
   - Outputs integrated datasets to `data/processed/integrated/`.
3. `03_features/01_feature_engineering.ipynb`
   - Creates model-ready features and the prediction target.
   - Outputs `data/processed/features/feature_engineered_dataset.csv`.
4. `04_modeling/`
   - Trains and compares volatility prediction models.
   - Outputs predictions and metrics to `data/processed/modeling/<model_name>/`.

## Modeling Notebooks

- `04_modeling/01_linear_regression.ipynb`
- `04_modeling/02_random_forest.ipynb`
- `04_modeling/03_gradient_boosting.ipynb`
- `04_modeling/04_ridge_regression.ipynb`

Each modeling notebook should save:

- `test_predictions.csv`
- `metrics.csv`

## Pathing

The notebooks use relative paths based on their current folders:

- Source notebooks use `../../../data/...`
- Integration, feature, and modeling notebooks use `../../data/...`

If a notebook is moved, its data paths need to be updated.

## Future Cleanup

If notebook code becomes important and reusable, move it into `src/` and import it from the notebooks. The notebooks should eventually focus on running the workflow and explaining results, not holding all project logic.
