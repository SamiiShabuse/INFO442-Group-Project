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
  05_model_comparison/
  06_portfolio_optimization/
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
4. `03_features/02_feature_selection.ipynb`
   - Selects the shared feature list used by the all-ticker regression models.
   - Outputs `data/processed/features/selected_features.csv`.
5. `04_modeling/`
   - Trains volatility prediction models.
   - Outputs predictions and metrics to `data/processed/modeling/<model_name>/`.
6. `05_model_comparison/01_model_comparison.ipynb`
   - Combines model metrics into dashboard-ready comparison tables.
   - Outputs files to `data/processed/model_comparison/`.
7. `06_portfolio_optimization/01_portfolio_optimization.ipynb`
   - Uses Random Forest predicted volatility with historical correlations to build predictive portfolio strategies.
   - Outputs performance metrics, strategy weights, daily returns, and cumulative returns to `data/processed/portfolio_optimization/`.

## Modeling Notebooks

- `04_modeling/01_linear_regression.ipynb`
- `04_modeling/02_random_forest.ipynb`
- `04_modeling/03_gradient_boosting.ipynb`
- `04_modeling/04_ridge_regression.ipynb`
- `04_modeling/05_garch_volatility_model.ipynb`
- `04_modeling/06_feature_selection_experiments.ipynb`

Linear Regression, Ridge Regression, Random Forest, and Gradient Boosting use the shared selected feature list from `data/processed/features/selected_features.csv`.

GARCH is a SPY-only statistical volatility model, so it is reported separately from the all-ticker regression models.

Each modeling notebook should save:

- `test_predictions.csv`
- `metrics.csv`

## Current Outputs

- Cleaned source datasets: `data/processed/source_data/`
- Integrated market, sector, and macro datasets: `data/processed/integrated/`
- Feature-engineered modeling data and selected features: `data/processed/features/`
- Model predictions and metrics: `data/processed/modeling/`
- Model comparison tables: `data/processed/model_comparison/`
- Portfolio optimization outputs: `data/processed/portfolio_optimization/`

## Pathing

The notebooks use relative paths based on their current folders:

- Source notebooks use `../../../data/...`
- Integration, feature, modeling, model comparison, and portfolio optimization notebooks use `../../data/...`

If a notebook is moved, its data paths need to be updated.

## Future Cleanup

If notebook code becomes important and reusable, move it into `src/` and import it from the notebooks. The notebooks should eventually focus on running the workflow and explaining results, not holding all project logic.
