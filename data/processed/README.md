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
- `model_comparison/`
  - Combined model comparison tables used by the dashboard.
- `portfolio_optimization/`
  - Portfolio strategy outputs, target weights, and dry-run rebalance orders.

Use `source_data/` for cleaned individual data sources. Use the other folders for project-level outputs that combine or model across sources.

## Important Generated Outputs

```text
features/latest_feature_snapshot.csv
    latest model-ready feature rows used by live prediction scripts

modeling/random_forest/rf_model.pkl
    exported Random Forest model used for live predictions

modeling/random_forest/live_predictions/
    latest and archived Random Forest prediction runs

modeling/random_forest/live_evaluation/
    completed-window and trailing-volatility evaluation outputs

portfolio_optimization/live_weights/
    optimized target weights from live Random Forest predictions

portfolio_optimization/paper_orders/
    dry-run buy/sell/hold order files
```
