# Modeling Notebooks

This folder contains the project's volatility prediction models and supporting
feature-selection experiments.

## Notebooks

- `01_linear_regression.ipynb`
- `02_random_forest.ipynb`
- `03_gradient_boosting.ipynb`
- `04_ridge_regression.ipynb`
- `05_garch_volatility_model.ipynb`
- `06_feature_selection_experiments.ipynb`
- `07_neural_network_mlp.ipynb`

The all-ticker regression models read from:

- `data/processed/features/feature_engineered_dataset.csv`
- `data/processed/features/selected_features.csv`

Each notebook writes model outputs to:

- `data/processed/modeling/<model_name>/test_predictions.csv`
- `data/processed/modeling/<model_name>/metrics.csv`

Run these after `notebooks/03_features/01_feature_engineering.ipynb`.

## Model Roles

- Linear Regression and Ridge Regression provide linear benchmarks.
- Random Forest and Gradient Boosting model nonlinear relationships.
- Neural Network MLP provides a separate nonlinear neural-network comparison.
- GARCH is a univariate statistical model for SPY only, so it is reported
  separately from the all-ticker models.

The tuned Random Forest is currently the strongest all-ticker model by MAE,
RMSE, and R2. Its predicted volatility is therefore used by the portfolio
optimization workflow. The MLP is included for model comparison and in the
dashboard Prediction Explorer, but it does not replace Random Forest in the
optimizer because its test performance is weaker.

After rerunning a model, rerun
`notebooks/05_model_comparison/01_model_comparison.ipynb` so the comparison
CSV files consumed by the dashboard are refreshed.
