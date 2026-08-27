# Notebooks Folder

This folder contains the main project workflow, organized in the order the pipeline should be run.

For the polished project overview, start with `../README.md`. For a deeper
explanation of how the notebook outputs connect to scripts, package code,
dashboard pages, live evaluation, and dry-run orders, see
`../docs/project_workflow.md`.

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
  07_live_model_evaluation/
  08_paper_trading/
  09_predictive_vs_historical/
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
   - Selects the shared feature list used by the all-ticker models.
   - Outputs `data/processed/features/selected_features.csv`.
5. `04_modeling/`
   - Trains the volatility prediction models.
   - Outputs predictions and metrics to `data/processed/modeling/<model_name>/`.
6. `05_model_comparison/01_model_comparison.ipynb`
   - Combines saved model metrics into dashboard-ready comparison tables.
   - Keeps the SPY-only GARCH results separate from the all-ticker models.
   - Outputs files to `data/processed/model_comparison/`.
7. `06_portfolio_optimization/01_portfolio_optimization.ipynb`
   - Uses Random Forest predicted volatility with historical correlations to build the first predictive portfolio strategies.
   - Outputs performance metrics, strategy weights, daily returns, and cumulative returns to `data/processed/portfolio_optimization/`.
8. `07_live_model_evaluation/01_live_rf_real_data_evaluation.ipynb`
   - Evaluates archived Random Forest live predictions against real market data.
   - Visualizes live prediction changes and completed 20-trading-day evaluation windows.
9. `08_paper_trading/01_rebalance_order_analysis.ipynb`
   - Analyzes dry-run rebalance orders created from optimized target weights.
   - Visualizes target weights, buy/sell/hold actions, order dollars, and portfolio concentration.
10. `09_predictive_vs_historical/01_rf_vs_baseline_portfolio_impact.ipynb`
   - Directly compares RF predicted volatility against a trailing-volatility baseline.
   - Runs the walk-forward portfolio-impact analysis, rebalance-frequency robustness sweep, and calibration check.
   - Outputs the definitive project result tables to `data/processed/predictive_vs_historical/`.

## Modeling Notebooks

- `04_modeling/01_linear_regression.ipynb`
- `04_modeling/02_random_forest.ipynb`
- `04_modeling/03_gradient_boosting.ipynb`
- `04_modeling/04_ridge_regression.ipynb`
- `04_modeling/05_garch_volatility_model.ipynb`
- `04_modeling/06_feature_selection_experiments.ipynb`
- `04_modeling/07_neural_network_mlp.ipynb`

Linear Regression, Ridge Regression, Random Forest, Gradient Boosting, and the
Neural Network MLP use the shared selected feature list from
`data/processed/features/selected_features.csv`.

GARCH is a SPY-only statistical volatility model, so it is reported separately
from the all-ticker models.

Random Forest is the exported live model because it has a repeatable training
artifact workflow and leakage-safe holdout performance above the
trailing-volatility baseline. Its refreshed holdout MAE is 0.00412 versus
0.00469 for the trailing-volatility baseline. Gradient Boosting and the MLP
remain comparison models in the dashboard Prediction Explorer.

Notebook 09 is the final portfolio-impact experiment. It should be used for
README, dashboard, report, and presentation claims because it compares the RF
risk model against a matched historical-volatility baseline under a
walk-forward rebalance design.

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
- Predictive-vs-historical outputs: `data/processed/predictive_vs_historical/`
- Random Forest live prediction/evaluation outputs: `data/processed/modeling/random_forest/`

## Pathing

The notebooks use relative paths based on their current folders:

- Source notebooks use `../../../data/...`
- Integration, feature, modeling, model comparison, portfolio optimization,
  live evaluation, paper-trading, and predictive-vs-historical notebooks use
  `../../data/...`

If a notebook is moved, its data paths need to be updated.

## Future Cleanup

If notebook code becomes important and reusable, move it into `src/` and import
it from the notebooks. The notebooks should eventually focus on running the
workflow and explaining results, not holding all project logic.
