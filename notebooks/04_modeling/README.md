# Modeling Notebooks

This folder contains the volatility prediction models.

## Notebooks

- `01_linear_regression.ipynb`
- `02_random_forest.ipynb`
- `03_gradient_boosting.ipynb`
- `04_ridge_regression.ipynb`

Each notebook reads from:

- `data/processed/features/feature_engineered_dataset.csv`

Each notebook writes model outputs to:

- `data/processed/modeling/<model_name>/test_predictions.csv`
- `data/processed/modeling/<model_name>/metrics.csv`

Run these after `notebooks/03_features/01_feature_engineering.ipynb`.
