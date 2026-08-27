# Dashboard

This folder contains the Streamlit dashboard for the project.

The dashboard is the presentation layer. It should read cleaned and generated
outputs from `data/processed/`; it should not become the place where data
cleaning, training, or portfolio optimization logic lives.

For the full project workflow, see `../README.md` and
`../docs/project_workflow.md`.

Run it from the project root with:

```bash
streamlit run dashboard/app.py
```

Live deployment:

```text
https://portfolio-volatility-optimizer.streamlit.app/
```

Install dashboard dependencies from the project root with:

```bash
pip install -r dashboard/requirements.txt
```

The dashboard uses cleaned project outputs from `data/processed/`, especially:

- `data/processed/integrated/`
- `data/processed/features/`
- `data/processed/modeling/`
- `data/processed/model_comparison/`
- `data/processed/predictive_vs_historical/`

## Current Pages

- Overview
- Model Comparison
- Prediction Explorer
- Predictive vs Historical
- Live Optimizer

## Model Connections

The Model Comparison page reads the refreshed comparison tables from
`data/processed/model_comparison/`. It includes Linear Regression, Ridge
Regression, Random Forest, Gradient Boosting, and Neural Network MLP. GARCH is
displayed separately because it was evaluated only on SPY.

The Prediction Explorer reads each model's `test_predictions.csv` file and
supports all five all-ticker models, including the MLP.

The Live Optimizer intentionally uses Random Forest predicted volatility
combined with historical correlations. Random Forest is used because it has a
repeatable artifact/export workflow and leakage-safe holdout performance above
the trailing-volatility baseline; the other models remain available for
comparison in the Prediction Explorer.

The Predictive vs Historical page reads notebook-09 outputs from
`data/processed/predictive_vs_historical/`. This is the dashboard's definitive
portfolio-impact view: RF forecast error versus a trailing-volatility baseline,
walk-forward cumulative performance, rebalance-frequency robustness, and
risk-model calibration.

The Live Optimizer is an interactive sandbox. It builds a user-selected
portfolio from one selected RF prediction date and compares that fixed
allocation against historical and equal-weight versions over the 2024+ test
period. Use the Predictive vs Historical page for the project conclusion.

## Refreshing Outputs

If feature engineering or model notebooks are rerun, rerun the downstream
notebooks in order before launching the dashboard:

1. `scripts/train_rf_model.py`
2. `notebooks/05_model_comparison/01_model_comparison.ipynb`
3. `notebooks/09_predictive_vs_historical/01_rf_vs_baseline_portfolio_impact.ipynb`

This keeps the dashboard tables and charts aligned with the newest model outputs.

If you only want to refresh the live Random Forest workflow, use:

```powershell
.\.venv\Scripts\python.exe scripts\refresh_latest_features.py

.\.venv\Scripts\python.exe scripts\generate_predictions.py `
  --model data\processed\modeling\random_forest\rf_model.pkl `
  --features data\processed\features\latest_feature_snapshot.csv `
  --selected-features data\processed\features\selected_features.csv `
  --out data\processed\modeling\random_forest\live_predictions\latest_preds.csv

.\.venv\Scripts\python.exe scripts\archive_predictions.py

.\.venv\Scripts\python.exe scripts\generate_rebalance_orders.py --portfolio-value 100000
```

## Notes

The dashboard should stay focused on presentation and interaction. Data cleaning, feature engineering, modeling, and portfolio optimization should continue to live in the notebooks and processed output files.
